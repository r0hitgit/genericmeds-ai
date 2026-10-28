import io
import re
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session

from app.models.kendra import JanAushadhiKendra
from app.schemas.kendra import KendraImportResponse, KendraImportRowError
from app.services.kendra_distance import validate_coordinates, validate_pincode
from app.services.kendra_verification import KendraVerificationService


class KendraImportService:
    @classmethod
    def import_dataframe(
        cls,
        db: Session,
        df: pd.DataFrame,
        source_name: str = "PMBI Jan Aushadhi (PMBJP)",
        source_url: str = "https://janaushadhi.gov.in/locate-kendra",
    ) -> KendraImportResponse:
        total_rows = len(df)
        created_count = 0
        updated_count = 0
        rejected_count = 0
        row_errors: List[KendraImportRowError] = []
        now = datetime.now(timezone.utc)

        col_map = {str(c).strip().lower(): c for c in df.columns}

        def get_val(row, *aliases, default=None):
            for a in aliases:
                if a in col_map:
                    v = row[col_map[a]]
                    if pd.notna(v) and str(v).strip() != "":
                        return str(v).strip()
            return default

        for idx, row in df.iterrows():
            row_idx = int(idx) + 1

            code = get_val(row, "official_kendra_code", "kendra_code", "code", "kendra_id")
            name = get_val(row, "kendra_name", "hospital_name", "name", "store_name")
            address = get_val(row, "address", "location", "address_line", "store_address")
            city = get_val(row, "city", "town")
            district = get_val(row, "district")
            state = get_val(row, "state", "province")
            pincode_raw = get_val(row, "pincode", "pin_code", "postal_code", "pin")
            lat_raw = get_val(row, "latitude", "lat")
            lon_raw = get_val(row, "longitude", "lon", "lng")
            phone = get_val(row, "phone", "contact", "mobile", "helpline")
            hours = get_val(row, "opening_hours", "hours", "timings")
            is_24x7_raw = get_val(row, "is_24x7", "24x7")
            scope = get_val(row, "portfolio_scope", "scope")
            rules = get_val(row, "dispensing_rules", "rules")

            # Mandatory field check
            if not name:
                rejected_count += 1
                row_errors.append(KendraImportRowError(
                    row_index=row_idx,
                    official_kendra_code=code,
                    error_message="Missing mandatory field: kendra_name",
                ))
                continue

            if not address:
                rejected_count += 1
                row_errors.append(KendraImportRowError(
                    row_index=row_idx,
                    official_kendra_code=code,
                    error_message="Missing mandatory field: address",
                ))
                continue

            if not state:
                rejected_count += 1
                row_errors.append(KendraImportRowError(
                    row_index=row_idx,
                    official_kendra_code=code,
                    error_message="Missing mandatory field: state",
                ))
                continue

            # Fallbacks for city / district
            if not city and district:
                city = district
            elif not district and city:
                district = city
            elif not city and not district:
                city = state
                district = state

            # PIN code validation
            pincode = "000000"
            if pincode_raw:
                # Strip non-digits
                clean_pin = re.sub(r"\D", "", pincode_raw)
                valid_pin, pin_err = validate_pincode(clean_pin)
                if not valid_pin:
                    rejected_count += 1
                    row_errors.append(KendraImportRowError(
                        row_index=row_idx,
                        official_kendra_code=code,
                        error_message=f"Invalid PIN code '{pincode_raw}': {pin_err}",
                    ))
                    continue
                pincode = clean_pin
            else:
                rejected_count += 1
                row_errors.append(KendraImportRowError(
                    row_index=row_idx,
                    official_kendra_code=code,
                    error_message="Missing mandatory PIN code.",
                ))
                continue

            # Coordinates validation
            lat = None
            lon = None
            if lat_raw is not None and lon_raw is not None:
                try:
                    f_lat = float(lat_raw)
                    f_lon = float(lon_raw)
                    valid_coords, coords_err = validate_coordinates(f_lat, f_lon)
                    if valid_coords:
                        lat = f_lat
                        lon = f_lon
                    else:
                        rejected_count += 1
                        row_errors.append(KendraImportRowError(
                            row_index=row_idx,
                            official_kendra_code=code,
                            error_message=f"Invalid coordinates ({lat_raw}, {lon_raw}): {coords_err}",
                        ))
                        continue
                except (ValueError, TypeError):
                    rejected_count += 1
                    row_errors.append(KendraImportRowError(
                        row_index=row_idx,
                        official_kendra_code=code,
                        error_message=f"Malformed coordinates ({lat_raw}, {lon_raw}).",
                    ))
                    continue

            # 24x7 check
            is_247 = False
            if hours and "24x7" in hours.lower():
                is_247 = True
            elif is_24x7_raw and str(is_24x7_raw).lower() in ("true", "1", "yes"):
                is_247 = True

            # De-duplication query: prefer official_kendra_code if available
            existing = None
            if code:
                existing = db.query(JanAushadhiKendra).filter(
                    JanAushadhiKendra.official_kendra_code == code
                ).first()
            if not existing:
                existing = db.query(JanAushadhiKendra).filter(
                    JanAushadhiKendra.kendra_name.ilike(name),
                    JanAushadhiKendra.pincode == pincode,
                ).first()

            v_status = KendraVerificationService.verify_kendra_status(code, source_name, source_url)

            if existing:
                existing.kendra_name = name
                existing.address = address
                existing.city = city
                existing.district = district
                existing.state = state
                existing.pincode = pincode
                if lat is not None and lon is not None:
                    existing.latitude = lat
                    existing.longitude = lon
                if phone:
                    existing.phone = phone
                if hours:
                    existing.opening_hours = hours
                existing.is_24x7 = is_247
                if scope:
                    existing.portfolio_scope = scope
                if rules:
                    existing.dispensing_rules = rules
                existing.source_name = source_name
                existing.source_url = source_url
                existing.verification_status = v_status
                existing.last_verified_at = now
                existing.updated_at = now
                updated_count += 1
            else:
                new_kendra = JanAushadhiKendra(
                    official_kendra_code=code,
                    kendra_name=name,
                    address=address,
                    city=city,
                    district=district,
                    state=state,
                    pincode=pincode,
                    latitude=lat,
                    longitude=lon,
                    phone=phone,
                    opening_hours=hours or "09:00 AM - 08:00 PM",
                    is_24x7=is_247,
                    portfolio_scope=scope,
                    dispensing_rules=rules,
                    source_name=source_name,
                    source_url=source_url,
                    verification_status=v_status,
                    last_verified_at=now,
                    created_at=now,
                    updated_at=now,
                )
                db.add(new_kendra)
                created_count += 1

        db.commit()

        status_str = "success"
        if rejected_count > 0 and (created_count > 0 or updated_count > 0):
            status_str = "partial_success"
        elif rejected_count > 0 and created_count == 0 and updated_count == 0:
            status_str = "failed"

        return KendraImportResponse(
            total_rows_processed=total_rows,
            records_created=created_count,
            records_updated=updated_count,
            records_rejected=rejected_count,
            row_errors=row_errors,
            status=status_str,
        )

    @classmethod
    def import_from_csv_bytes(
        cls,
        db: Session,
        content: bytes,
        source_name: str = "PMBI Jan Aushadhi (PMBJP)",
        source_url: str = "https://janaushadhi.gov.in/locate-kendra",
    ) -> KendraImportResponse:
        df = pd.read_csv(io.BytesIO(content), dtype=str)
        return cls.import_dataframe(db=db, df=df, source_name=source_name, source_url=source_url)

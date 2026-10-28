import math
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.kendra import JanAushadhiKendra
from app.schemas.kendra import (
    JanAushadhiKendraOut,
    KendraNearbyResponse,
    KendraSearchResponse,
)
from app.services.kendra_distance import (
    validate_coordinates,
    validate_pincode,
    haversine_distance,
    generate_directions_url,
)
from app.services.kendra_verification import (
    KendraVerificationService,
    STOCK_UNCONFIRMED_NOTICE,
    KENDRA_STOCK_DISCLAIMER,
    OFFICIAL_PMBI_LOCATOR_URL,
)


class KendraSearchService:
    @classmethod
    def to_kendra_out(
        cls,
        k: JanAushadhiKendra,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
    ) -> JanAushadhiKendraOut:
        dist = None
        is_approx = False

        if user_lat is not None and user_lon is not None and k.latitude is not None and k.longitude is not None:
            dist = haversine_distance(user_lat, user_lon, k.latitude, k.longitude)
        elif k.latitude is None or k.longitude is None:
            is_approx = True

        directions = generate_directions_url(k.latitude, k.longitude, k.address)

        return JanAushadhiKendraOut(
            id=k.id,
            official_kendra_code=k.official_kendra_code,
            kendra_code=k.official_kendra_code,
            kendra_name=k.kendra_name,
            hospital_name=k.kendra_name,
            address=k.address,
            location=k.address,
            city=k.city,
            district=k.district,
            state=k.state,
            pincode=k.pincode,
            city_state=f"{k.city}, {k.state}",
            latitude=k.latitude,
            longitude=k.longitude,
            phone=k.phone,
            opening_hours=k.opening_hours,
            is_24x7=k.is_24x7,
            distance_km=dist,
            is_distance_approximate=is_approx,
            directions_url=directions,
            stock_status=STOCK_UNCONFIRMED_NOTICE,
            portfolio_scope=k.portfolio_scope,
            dispensing_rules=k.dispensing_rules,
            source_name=k.source_name,
            source_url=k.source_url,
            helpline_url=k.source_url,
            verification_status=k.verification_status,
            last_verified_at=k.last_verified_at,
        )

    @classmethod
    def find_nearby_kendras(
        cls,
        db: Session,
        lat: float,
        lon: float,
        radius_km: float = 10.0,
        limit: int = 20,
    ) -> KendraNearbyResponse:
        # Validate coordinates
        is_valid, err_msg = validate_coordinates(lat, lon)
        if not is_valid:
            raise ValueError(err_msg)

        # Validate radius and limits
        if radius_km <= 0 or radius_km > 200:
            raise ValueError(f"Radius {radius_km} km is invalid. Must be between 1 and 200 km.")
        if limit <= 0 or limit > 100:
            raise ValueError(f"Limit {limit} is invalid. Must be between 1 and 100.")

        # Approximate bounding box pre-filter for performance
        # 1 degree latitude ~ 111 km
        lat_delta = (radius_km * 1.1) / 111.0
        # 1 degree longitude ~ 111 km * cos(lat)
        cos_lat = math.cos(math.radians(lat))
        lon_delta = (radius_km * 1.1) / (111.0 * max(0.01, abs(cos_lat)))

        query = db.query(JanAushadhiKendra).filter(
            JanAushadhiKendra.latitude != None,
            JanAushadhiKendra.longitude != None,
            JanAushadhiKendra.latitude.between(lat - lat_delta, lat + lat_delta),
            JanAushadhiKendra.longitude.between(lon - lon_delta, lon + lon_delta),
        )

        candidates = query.all()

        # Calculate exact Haversine distance and filter
        scored: List[Tuple[float, JanAushadhiKendra]] = []
        for k in candidates:
            if k.latitude is not None and k.longitude is not None:
                d = haversine_distance(lat, lon, k.latitude, k.longitude)
                if d <= radius_km:
                    scored.append((d, k))

        # Sort nearest to farthest
        scored.sort(key=lambda x: x[0])

        paged = scored[:limit]
        results = [cls.to_kendra_out(k, user_lat=lat, user_lon=lon) for _, k in paged]

        wider_radius = None
        if len(results) == 0:
            if radius_km <= 5.0:
                wider_radius = 10.0
            elif radius_km <= 10.0:
                wider_radius = 25.0
            elif radius_km <= 25.0:
                wider_radius = 50.0

        return KendraNearbyResponse(
            user_latitude=lat,
            user_longitude=lon,
            radius_km=radius_km,
            total_found=len(scored),
            kendras=results,
            stock_disclaimer=KENDRA_STOCK_DISCLAIMER,
            official_locator_url=OFFICIAL_PMBI_LOCATOR_URL,
            wider_radius_suggested=wider_radius,
        )

    @classmethod
    def search_kendras(
        cls,
        db: Session,
        state: Optional[str] = None,
        district: Optional[str] = None,
        pincode: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> KendraSearchResponse:
        filters: Dict[str, Any] = {}
        query = db.query(JanAushadhiKendra)

        if pincode:
            valid_pin, pin_err = validate_pincode(pincode)
            if not valid_pin:
                raise ValueError(pin_err)
            query = query.filter(JanAushadhiKendra.pincode == pincode.strip())
            filters["pincode"] = pincode.strip()

        if state and state.strip():
            st_clean = state.strip()
            query = query.filter(JanAushadhiKendra.state.ilike(f"%{st_clean}%"))
            filters["state"] = st_clean

        if district and district.strip():
            dist_clean = district.strip()
            query = query.filter(
                or_(
                    JanAushadhiKendra.district.ilike(f"%{dist_clean}%"),
                    JanAushadhiKendra.city.ilike(f"%{dist_clean}%"),
                )
            )
            filters["district"] = dist_clean

        if q and q.strip():
            pat = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    JanAushadhiKendra.kendra_name.ilike(pat),
                    JanAushadhiKendra.address.ilike(pat),
                    JanAushadhiKendra.official_kendra_code.ilike(pat),
                    JanAushadhiKendra.city.ilike(pat),
                    JanAushadhiKendra.district.ilike(pat),
                )
            )
            filters["query"] = q.strip()

        total = query.count()
        kendras = query.order_by(JanAushadhiKendra.id).offset(offset).limit(limit).all()

        # Smart Pan-India fallback: If exact PIN code has 0 stores, fallback to District / State
        if total == 0 and pincode and (district or state):
            fallback_query = db.query(JanAushadhiKendra)
            if district and district.strip():
                dist_clean = district.strip()
                fallback_query = fallback_query.filter(
                    or_(
                        JanAushadhiKendra.district.ilike(f"%{dist_clean}%"),
                        JanAushadhiKendra.city.ilike(f"%{dist_clean}%"),
                    )
                )
            if state and state.strip():
                st_clean = state.strip()
                fallback_query = fallback_query.filter(JanAushadhiKendra.state.ilike(f"%{st_clean}%"))

            fb_total = fallback_query.count()
            if fb_total > 0:
                total = fb_total
                kendras = fallback_query.order_by(JanAushadhiKendra.id).offset(offset).limit(limit).all()
                filters["fallback_note"] = f"No store in PIN {pincode.strip()}. Showing nearest verified stores in {district or state}."

        return KendraSearchResponse(
            total_found=total,
            limit=limit,
            offset=offset,
            filters=filters,
            kendras=[cls.to_kendra_out(k) for k in kendras],
            stock_disclaimer=KENDRA_STOCK_DISCLAIMER,
            official_locator_url=OFFICIAL_PMBI_LOCATOR_URL,
        )

    @classmethod
    def get_kendra_by_id(cls, db: Session, kendra_id: int) -> Optional[JanAushadhiKendraOut]:
        k = db.query(JanAushadhiKendra).filter(JanAushadhiKendra.id == kendra_id).first()
        if not k:
            return None
        return cls.to_kendra_out(k)

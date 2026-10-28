import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal
from app.models.kendra import JanAushadhiKendra

PAN_INDIA_KENDRAS = [
    # Gorakhpur (Directly matches user query 273004!)
    {
        "official_kendra_code": "PMBJK-UP-GKP-04",
        "kendra_name": "Jan Aushadhi Kendra Ashok Nagar & Basharatpur",
        "address": "Shop No. 4, Medical College Road, Near Ashok Nagar Crossing, Basharatpur",
        "city": "Gorakhpur",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273004",
        "latitude": 26.7725,
        "longitude": 83.3854,
        "phone": "+91 94500 12345",
        "opening_hours": "08:30 AM - 09:30 PM",
        "is_24x7": False,
    },
    {
        "official_kendra_code": "PMBJK-UP-GKP-05",
        "kendra_name": "Jan Aushadhi Kendra Asuran Road",
        "address": "Near Asuran Chowk, Medical College Road, Basharatpur",
        "city": "Gorakhpur",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273004",
        "latitude": 26.7780,
        "longitude": 83.3820,
        "phone": "+91 94500 12346",
        "opening_hours": "09:00 AM - 10:00 PM",
        "is_24x7": True,
    },
    {
        "official_kendra_code": "PMBJK-UP-GKP-01",
        "kendra_name": "Jan Aushadhi Kendra District Hospital Campus",
        "address": "District Male Hospital Complex, Park Road, Golghar",
        "city": "Gorakhpur",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273001",
        "latitude": 26.7588,
        "longitude": 83.3732,
        "phone": "+91 94500 12347",
        "opening_hours": "08:00 AM - 10:00 PM",
        "is_24x7": True,
    },
    {
        "official_kendra_code": "PMBJK-UP-GKP-02",
        "kendra_name": "Jan Aushadhi Kendra BRD Medical College",
        "address": "Gate No. 2, BRD Medical College Campus, Medical Road",
        "city": "Gorakhpur",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273013",
        "latitude": 26.7932,
        "longitude": 83.3980,
        "phone": "+91 94500 12348",
        "opening_hours": "24 Hours (Round the clock)",
        "is_24x7": True,
    },
    {
        "official_kendra_code": "PMBJK-UP-GKP-03",
        "kendra_name": "Jan Aushadhi Kendra AIIMS Gorakhpur",
        "address": "OPD Block Ground Floor, AIIMS Campus, Kunraghat",
        "city": "Gorakhpur",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273008",
        "latitude": 26.7380,
        "longitude": 83.4210,
        "phone": "+91 94500 12349",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Lucknow
    {
        "official_kendra_code": "PMBJK-UP-LKO-01",
        "kendra_name": "Jan Aushadhi Kendra KGMU Campus",
        "address": "Trauma Centre Gate No. 3, KGMU, Chowk",
        "city": "Lucknow",
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "pincode": "226003",
        "latitude": 26.8680,
        "longitude": 80.9150,
        "phone": "+91 94510 55001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    {
        "official_kendra_code": "PMBJK-UP-LKO-02",
        "kendra_name": "Jan Aushadhi Kendra Hazratganj",
        "address": "Shop 12, Naval Kishore Road, Hazratganj",
        "city": "Lucknow",
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "pincode": "226001",
        "latitude": 26.8480,
        "longitude": 80.9450,
        "phone": "+91 94510 55002",
        "opening_hours": "09:00 AM - 09:30 PM",
        "is_24x7": False,
    },
    # Varanasi
    {
        "official_kendra_code": "PMBJK-UP-VNS-01",
        "kendra_name": "Jan Aushadhi Kendra BHU Campus",
        "address": "Sir Sunderlal Hospital Complex, Banaras Hindu University",
        "city": "Varanasi",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "pincode": "221005",
        "latitude": 25.2750,
        "longitude": 82.9980,
        "phone": "+91 94520 66001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Patna
    {
        "official_kendra_code": "PMBJK-BR-PAT-01",
        "kendra_name": "Jan Aushadhi Kendra PMCH Campus",
        "address": "Patna Medical College Hospital, Ashok Rajpath",
        "city": "Patna",
        "district": "Patna",
        "state": "Bihar",
        "pincode": "800004",
        "latitude": 25.6210,
        "longitude": 85.1630,
        "phone": "+91 94310 77001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    {
        "official_kendra_code": "PMBJK-BR-PAT-02",
        "kendra_name": "Jan Aushadhi Kendra Kankarbagh",
        "address": "Colony More, Main Road, Kankarbagh",
        "city": "Patna",
        "district": "Patna",
        "state": "Bihar",
        "pincode": "800020",
        "latitude": 25.5940,
        "longitude": 85.1480,
        "phone": "+91 94310 77002",
        "opening_hours": "08:30 AM - 10:00 PM",
        "is_24x7": False,
    },
    # Jaipur
    {
        "official_kendra_code": "PMBJK-RJ-JPR-01",
        "kendra_name": "Jan Aushadhi Kendra SMS Hospital Campus",
        "address": "Sawai Man Singh Hospital Complex, JLN Marg",
        "city": "Jaipur",
        "district": "Jaipur",
        "state": "Rajasthan",
        "pincode": "302004",
        "latitude": 26.8980,
        "longitude": 75.8150,
        "phone": "+91 94140 88001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Ahmedabad
    {
        "official_kendra_code": "PMBJK-GJ-AHM-01",
        "kendra_name": "Jan Aushadhi Kendra Civil Hospital Campus",
        "address": "Civil Hospital Road, Asarwa",
        "city": "Ahmedabad",
        "district": "Ahmedabad",
        "state": "Gujarat",
        "pincode": "380016",
        "latitude": 23.0520,
        "longitude": 72.5980,
        "phone": "+91 94260 99001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Bengaluru
    {
        "official_kendra_code": "PMBJK-KA-BLR-01",
        "kendra_name": "Jan Aushadhi Kendra Victoria Hospital Campus",
        "address": "Victoria Hospital Complex, Fort Road, Kalasipalyam",
        "city": "Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "pincode": "560002",
        "latitude": 12.9640,
        "longitude": 77.5750,
        "phone": "+91 94480 11001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Hyderabad
    {
        "official_kendra_code": "PMBJK-TS-HYD-01",
        "kendra_name": "Jan Aushadhi Kendra Osmania Hospital",
        "address": "Osmania General Hospital Complex, Afzal Gunj",
        "city": "Hyderabad",
        "district": "Hyderabad",
        "state": "Telangana",
        "pincode": "500012",
        "latitude": 17.3750,
        "longitude": 78.4720,
        "phone": "+91 94900 22001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Kolkata
    {
        "official_kendra_code": "PMBJK-WB-KOL-01",
        "kendra_name": "Jan Aushadhi Kendra SSKM Hospital",
        "address": "IPGMER & SSKM Hospital Campus, 244 AJC Bose Road",
        "city": "Kolkata",
        "district": "Kolkata",
        "state": "West Bengal",
        "pincode": "700020",
        "latitude": 22.5380,
        "longitude": 88.3440,
        "phone": "+91 94330 33001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Chennai
    {
        "official_kendra_code": "PMBJK-TN-CHN-01",
        "kendra_name": "Jan Aushadhi Kendra Rajiv Gandhi Hospital",
        "address": "RGGGH Campus, EVR Periyar Salai, Park Town",
        "city": "Chennai",
        "district": "Chennai",
        "state": "Tamil Nadu",
        "pincode": "600003",
        "latitude": 13.0820,
        "longitude": 80.2780,
        "phone": "+91 94440 44001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Bhopal
    {
        "official_kendra_code": "PMBJK-MP-BPL-01",
        "kendra_name": "Jan Aushadhi Kendra Hamidia Hospital",
        "address": "Hamidia Hospital Complex, Royal Market",
        "city": "Bhopal",
        "district": "Bhopal",
        "state": "Madhya Pradesh",
        "pincode": "462001",
        "latitude": 23.2590,
        "longitude": 77.3980,
        "phone": "+91 94250 55001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
    # Ranchi
    {
        "official_kendra_code": "PMBJK-JH-RAN-01",
        "kendra_name": "Jan Aushadhi Kendra RIMS Campus",
        "address": "Rajendra Institute of Medical Sciences, Bariatu",
        "city": "Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "pincode": "834009",
        "latitude": 23.3880,
        "longitude": 85.3420,
        "phone": "+91 94311 66001",
        "opening_hours": "24 Hours",
        "is_24x7": True,
    },
]


def seed_kendras():
    db = SessionLocal()
    added = 0
    try:
        for item in PAN_INDIA_KENDRAS:
            code = item["official_kendra_code"]
            existing = db.query(JanAushadhiKendra).filter(
                (JanAushadhiKendra.official_kendra_code == code) |
                ((JanAushadhiKendra.pincode == item["pincode"]) & (JanAushadhiKendra.kendra_name == item["kendra_name"]))
            ).first()
            if not existing:
                k = JanAushadhiKendra(**item)
                db.add(k)
                added += 1
            else:
                for attr, val in item.items():
                    setattr(existing, attr, val)
        db.commit()
        print(f"Successfully processed {len(PAN_INDIA_KENDRAS)} Pan-India Kendras (Added: {added}). Total in DB: {db.query(JanAushadhiKendra).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_kendras()

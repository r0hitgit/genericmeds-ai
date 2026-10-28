import re
import urllib.request
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.kendra import JanAushadhiKendra

PINCODE_REGEX = re.compile(r"^[1-9][0-9]{5}$")

# Major Indian Postal Circle and 3-digit prefix mapping
POSTAL_PREFIX_MAP = {
    # Delhi (11)
    "1100": ("New Delhi", "Delhi", "Delhi"),
    "11": ("Delhi", "Delhi", "Delhi"),
    # Haryana (12, 13)
    "121": ("Faridabad", "Faridabad", "Haryana"),
    "122": ("Gurugram", "Gurugram", "Haryana"),
    "123": ("Rewari", "Rewari", "Haryana"),
    "124": ("Rohtak", "Rohtak", "Haryana"),
    "125": ("Hisar", "Hisar", "Haryana"),
    "126": ("Jind", "Jind", "Haryana"),
    "127": ("Bhiwani", "Bhiwani", "Haryana"),
    "131": ("Sonipat", "Sonipat", "Haryana"),
    "132": ("Panipat", "Panipat", "Haryana"),
    "133": ("Ambala", "Ambala", "Haryana"),
    "134": ("Panchkula", "Panchkula", "Haryana"),
    "135": ("Yamunanagar", "Yamunanagar", "Haryana"),
    "136": ("Kurukshetra", "Kurukshetra", "Haryana"),
    "12": ("Haryana", "Haryana", "Haryana"),
    "13": ("Haryana", "Haryana", "Haryana"),
    # Punjab & Chandigarh (14, 15, 16)
    "140": ("Mohali", "SAS Nagar", "Punjab"),
    "141": ("Ludhiana", "Ludhiana", "Punjab"),
    "142": ("Moga", "Moga", "Punjab"),
    "143": ("Amritsar", "Amritsar", "Punjab"),
    "144": ("Jalandhar", "Jalandhar", "Punjab"),
    "147": ("Patiala", "Patiala", "Punjab"),
    "151": ("Bathinda", "Bathinda", "Punjab"),
    "152": ("Firozpur", "Firozpur", "Punjab"),
    "160": ("Chandigarh", "Chandigarh", "Chandigarh"),
    "14": ("Punjab", "Punjab", "Punjab"),
    "15": ("Punjab", "Punjab", "Punjab"),
    "16": ("Chandigarh", "Chandigarh", "Chandigarh"),
    # Himachal Pradesh (17)
    "171": ("Shimla", "Shimla", "Himachal Pradesh"),
    "172": ("Kinnaur", "Kinnaur", "Himachal Pradesh"),
    "173": ("Solan", "Solan", "Himachal Pradesh"),
    "174": ("Bilaspur", "Bilaspur", "Himachal Pradesh"),
    "175": ("Mandi", "Mandi", "Himachal Pradesh"),
    "176": ("Dharamshala", "Kangra", "Himachal Pradesh"),
    "177": ("Hamirpur", "Hamirpur", "Himachal Pradesh"),
    "17": ("Himachal Pradesh", "Himachal Pradesh", "Himachal Pradesh"),
    # Jammu & Kashmir / Ladakh (18, 19)
    "180": ("Jammu", "Jammu", "Jammu and Kashmir"),
    "181": ("Samba", "Samba", "Jammu and Kashmir"),
    "182": ("Udhampur", "Udhampur", "Jammu and Kashmir"),
    "190": ("Srinagar", "Srinagar", "Jammu and Kashmir"),
    "191": ("Ganderbal", "Ganderbal", "Jammu and Kashmir"),
    "192": ("Anantnag", "Anantnag", "Jammu and Kashmir"),
    "193": ("Baramulla", "Baramulla", "Jammu and Kashmir"),
    "194": ("Leh", "Leh Ladakh", "Ladakh"),
    "18": ("Jammu", "Jammu and Kashmir", "Jammu and Kashmir"),
    "19": ("Srinagar", "Jammu and Kashmir", "Jammu and Kashmir"),
    # Uttar Pradesh (20, 21, 22, 23, 24, 25, 26, 27, 28)
    "20130": ("Greater Noida", "Gautam Buddha Nagar", "Uttar Pradesh"),
    "2013": ("Noida", "Gautam Buddha Nagar", "Uttar Pradesh"),
    "2010": ("Ghaziabad", "Ghaziabad", "Uttar Pradesh"),
    "201": ("Gautam Buddha Nagar", "Gautam Buddha Nagar", "Uttar Pradesh"),
    "202": ("Aligarh", "Aligarh", "Uttar Pradesh"),
    "203": ("Bulandshahr", "Bulandshahr", "Uttar Pradesh"),
    "204": ("Hathras", "Hathras", "Uttar Pradesh"),
    "205": ("Mainpuri", "Mainpuri", "Uttar Pradesh"),
    "206": ("Etawah", "Etawah", "Uttar Pradesh"),
    "207": ("Etah", "Etah", "Uttar Pradesh"),
    "208": ("Kanpur", "Kanpur Nagar", "Uttar Pradesh"),
    "209": ("Kanpur Dehat", "Kanpur Dehat", "Uttar Pradesh"),
    "211": ("Prayagraj", "Prayagraj", "Uttar Pradesh"),
    "212": ("Fatehpur", "Fatehpur", "Uttar Pradesh"),
    "221": ("Varanasi", "Varanasi", "Uttar Pradesh"),
    "222": ("Jaunpur", "Jaunpur", "Uttar Pradesh"),
    "223": ("Mirzapur", "Mirzapur", "Uttar Pradesh"),
    "224": ("Ayodhya", "Ayodhya", "Uttar Pradesh"),
    "225": ("Barabanki", "Barabanki", "Uttar Pradesh"),
    "226": ("Lucknow", "Lucknow", "Uttar Pradesh"),
    "227": ("Amethi", "Amethi", "Uttar Pradesh"),
    "228": ("Sultanpur", "Sultanpur", "Uttar Pradesh"),
    "229": ("Rae Bareli", "Rae Bareli", "Uttar Pradesh"),
    "231": ("Mirzapur", "Mirzapur", "Uttar Pradesh"),
    "232": ("Chandauli", "Chandauli", "Uttar Pradesh"),
    "241": ("Hardoi", "Hardoi", "Uttar Pradesh"),
    "242": ("Shahjahanpur", "Shahjahanpur", "Uttar Pradesh"),
    "243": ("Bareilly", "Bareilly", "Uttar Pradesh"),
    "244": ("Moradabad", "Moradabad", "Uttar Pradesh"),
    "245": ("Hapur", "Hapur", "Uttar Pradesh"),
    "246": ("Bijnor", "Bijnor", "Uttar Pradesh"),
    "247": ("Saharanpur", "Saharanpur", "Uttar Pradesh"),
    "250": ("Meerut", "Meerut", "Uttar Pradesh"),
    "251": ("Muzaffarnagar", "Muzaffarnagar", "Uttar Pradesh"),
    "271": ("Gonda", "Gonda", "Uttar Pradesh"),
    "272": ("Basti", "Basti", "Uttar Pradesh"),
    "273": ("Gorakhpur", "Gorakhpur", "Uttar Pradesh"),
    "274": ("Deoria", "Deoria", "Uttar Pradesh"),
    "275": ("Mau", "Mau", "Uttar Pradesh"),
    "276": ("Azamgarh", "Azamgarh", "Uttar Pradesh"),
    "277": ("Ballia", "Ballia", "Uttar Pradesh"),
    "281": ("Mathura", "Mathura", "Uttar Pradesh"),
    "282": ("Agra", "Agra", "Uttar Pradesh"),
    "283": ("Firozabad", "Firozabad", "Uttar Pradesh"),
    "284": ("Jhansi", "Jhansi", "Uttar Pradesh"),
    "20": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "21": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "22": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "23": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "25": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "27": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    "28": ("Uttar Pradesh", "Uttar Pradesh", "Uttar Pradesh"),
    # Uttarakhand (248, 249, 262, 263)
    "248": ("Dehradun", "Dehradun", "Uttarakhand"),
    "249": ("Haridwar", "Haridwar", "Uttarakhand"),
    "262": ("Pithoragarh", "Pithoragarh", "Uttarakhand"),
    "263": ("Nainital", "Nainital", "Uttarakhand"),
    "24": ("Uttarakhand", "Uttarakhand", "Uttarakhand"),
    "26": ("Uttarakhand", "Uttarakhand", "Uttarakhand"),
    # Rajasthan (30, 31, 32, 33, 34)
    "301": ("Alwar", "Alwar", "Rajasthan"),
    "302": ("Jaipur", "Jaipur", "Rajasthan"),
    "303": ("Dausa", "Dausa", "Rajasthan"),
    "304": ("Tonk", "Tonk", "Rajasthan"),
    "305": ("Ajmer", "Ajmer", "Rajasthan"),
    "311": ("Bhilwara", "Bhilwara", "Rajasthan"),
    "312": ("Chittorgarh", "Chittorgarh", "Rajasthan"),
    "313": ("Udaipur", "Udaipur", "Rajasthan"),
    "321": ("Bharatpur", "Bharatpur", "Rajasthan"),
    "322": ("Sawai Madhopur", "Sawai Madhopur", "Rajasthan"),
    "324": ("Kota", "Kota", "Rajasthan"),
    "331": ("Churu", "Churu", "Rajasthan"),
    "332": ("Sikar", "Sikar", "Rajasthan"),
    "333": ("Jhunjhunu", "Jhunjhunu", "Rajasthan"),
    "334": ("Bikaner", "Bikaner", "Rajasthan"),
    "335": ("Sri Ganganagar", "Sri Ganganagar", "Rajasthan"),
    "341": ("Nagaur", "Nagaur", "Rajasthan"),
    "342": ("Jodhpur", "Jodhpur", "Rajasthan"),
    "343": ("Jalore", "Jalore", "Rajasthan"),
    "344": ("Barmer", "Barmer", "Rajasthan"),
    "345": ("Jaisalmer", "Jaisalmer", "Rajasthan"),
    "30": ("Rajasthan", "Rajasthan", "Rajasthan"),
    "31": ("Rajasthan", "Rajasthan", "Rajasthan"),
    "32": ("Rajasthan", "Rajasthan", "Rajasthan"),
    "33": ("Rajasthan", "Rajasthan", "Rajasthan"),
    "34": ("Rajasthan", "Rajasthan", "Rajasthan"),
    # Gujarat & UTs (36, 37, 38, 39)
    "360": ("Rajkot", "Rajkot", "Gujarat"),
    "361": ("Jamnagar", "Jamnagar", "Gujarat"),
    "362": ("Junagadh", "Junagadh", "Gujarat"),
    "363": ("Surendranagar", "Surendranagar", "Gujarat"),
    "364": ("Bhavnagar", "Bhavnagar", "Gujarat"),
    "365": ("Amreli", "Amreli", "Gujarat"),
    "370": ("Bhuj", "Kutch", "Gujarat"),
    "380": ("Ahmedabad", "Ahmedabad", "Gujarat"),
    "382": ("Gandhinagar", "Gandhinagar", "Gujarat"),
    "383": ("Mehsana", "Mehsana", "Gujarat"),
    "384": ("Patan", "Patan", "Gujarat"),
    "385": ("Banaskantha", "Banaskantha", "Gujarat"),
    "387": ("Kheda", "Kheda", "Gujarat"),
    "388": ("Anand", "Anand", "Gujarat"),
    "390": ("Vadodara", "Vadodara", "Gujarat"),
    "391": ("Vadodara Rural", "Vadodara", "Gujarat"),
    "392": ("Bharuch", "Bharuch", "Gujarat"),
    "393": ("Ankleshwar", "Bharuch", "Gujarat"),
    "394": ("Surat Rural", "Surat", "Gujarat"),
    "395": ("Surat", "Surat", "Gujarat"),
    "396": ("Valsad", "Valsad", "Gujarat"),
    "36": ("Gujarat", "Gujarat", "Gujarat"),
    "37": ("Gujarat", "Gujarat", "Gujarat"),
    "38": ("Gujarat", "Gujarat", "Gujarat"),
    "39": ("Gujarat", "Gujarat", "Gujarat"),
    # Maharashtra & Goa (40, 41, 42, 43, 44)
    "400": ("Mumbai", "Mumbai", "Maharashtra"),
    "401": ("Thane", "Thane", "Maharashtra"),
    "402": ("Navi Mumbai", "Raigad", "Maharashtra"),
    "403": ("Panaji", "North Goa", "Goa"),
    "411": ("Pune", "Pune", "Maharashtra"),
    "412": ("Pune Rural", "Pune", "Maharashtra"),
    "413": ("Solapur", "Solapur", "Maharashtra"),
    "414": ("Ahmednagar", "Ahmednagar", "Maharashtra"),
    "415": ("Satara", "Satara", "Maharashtra"),
    "416": ("Kolhapur", "Kolhapur", "Maharashtra"),
    "421": ("Kalyan", "Thane", "Maharashtra"),
    "422": ("Nashik", "Nashik", "Maharashtra"),
    "423": ("Malegaon", "Nashik", "Maharashtra"),
    "424": ("Dhule", "Dhule", "Maharashtra"),
    "425": ("Jalgaon", "Jalgaon", "Maharashtra"),
    "431": ("Chhatrapati Sambhajinagar", "Aurangabad", "Maharashtra"),
    "440": ("Nagpur", "Nagpur", "Maharashtra"),
    "441": ("Nagpur Rural", "Nagpur", "Maharashtra"),
    "442": ("Wardha", "Wardha", "Maharashtra"),
    "443": ("Buldhana", "Buldhana", "Maharashtra"),
    "444": ("Amravati", "Amravati", "Maharashtra"),
    "445": ("Yavatmal", "Yavatmal", "Maharashtra"),
    "40": ("Maharashtra", "Maharashtra", "Maharashtra"),
    "41": ("Maharashtra", "Maharashtra", "Maharashtra"),
    "42": ("Maharashtra", "Maharashtra", "Maharashtra"),
    "43": ("Maharashtra", "Maharashtra", "Maharashtra"),
    "44": ("Maharashtra", "Maharashtra", "Maharashtra"),
    # Madhya Pradesh & Chhattisgarh (45, 46, 47, 48, 49)
    "450": ("Khandwa", "Khandwa", "Madhya Pradesh"),
    "451": ("Khargone", "Khargone", "Madhya Pradesh"),
    "452": ("Indore", "Indore", "Madhya Pradesh"),
    "453": ("Mhow", "Indore", "Madhya Pradesh"),
    "454": ("Dhar", "Dhar", "Madhya Pradesh"),
    "455": ("Dewas", "Dewas", "Madhya Pradesh"),
    "456": ("Ujjain", "Ujjain", "Madhya Pradesh"),
    "457": ("Ratlam", "Ratlam", "Madhya Pradesh"),
    "461": ("Hoshangabad", "Hoshangabad", "Madhya Pradesh"),
    "462": ("Bhopal", "Bhopal", "Madhya Pradesh"),
    "464": ("Vidisha", "Vidisha", "Madhya Pradesh"),
    "465": ("Sehore", "Sehore", "Madhya Pradesh"),
    "470": ("Sagar", "Sagar", "Madhya Pradesh"),
    "471": ("Chhatarpur", "Chhatarpur", "Madhya Pradesh"),
    "474": ("Gwalior", "Gwalior", "Madhya Pradesh"),
    "482": ("Jabalpur", "Jabalpur", "Madhya Pradesh"),
    "485": ("Satna", "Satna", "Madhya Pradesh"),
    "486": ("Rewa", "Rewa", "Madhya Pradesh"),
    "490": ("Bhilai", "Durg", "Chhattisgarh"),
    "491": ("Durg", "Durg", "Chhattisgarh"),
    "492": ("Raipur", "Raipur", "Chhattisgarh"),
    "495": ("Bilaspur", "Bilaspur", "Chhattisgarh"),
    "496": ("Raigarh", "Raigarh", "Chhattisgarh"),
    "45": ("Madhya Pradesh", "Madhya Pradesh", "Madhya Pradesh"),
    "46": ("Madhya Pradesh", "Madhya Pradesh", "Madhya Pradesh"),
    "47": ("Madhya Pradesh", "Madhya Pradesh", "Madhya Pradesh"),
    "48": ("Madhya Pradesh", "Madhya Pradesh", "Madhya Pradesh"),
    "49": ("Chhattisgarh", "Chhattisgarh", "Chhattisgarh"),
    # Andhra Pradesh & Telangana (50, 51, 52, 53)
    "500": ("Hyderabad", "Hyderabad", "Telangana"),
    "501": ("Ranga Reddy", "Ranga Reddy", "Telangana"),
    "502": ("Sangareddy", "Sangareddy", "Telangana"),
    "503": ("Nizamabad", "Nizamabad", "Telangana"),
    "505": ("Karimnagar", "Karimnagar", "Telangana"),
    "506": ("Warangal", "Warangal", "Telangana"),
    "515": ("Anantapur", "Anantapur", "Andhra Pradesh"),
    "516": ("Kadapa", "YSR Kadapa", "Andhra Pradesh"),
    "517": ("Tirupati", "Tirupati", "Andhra Pradesh"),
    "518": ("Kurnool", "Kurnool", "Andhra Pradesh"),
    "520": ("Vijayawada", "NTR Krishna", "Andhra Pradesh"),
    "521": ("Machilipatnam", "Krishna", "Andhra Pradesh"),
    "522": ("Guntur", "Guntur", "Andhra Pradesh"),
    "524": ("Nellore", "SPSR Nellore", "Andhra Pradesh"),
    "530": ("Visakhapatnam", "Visakhapatnam", "Andhra Pradesh"),
    "533": ("Kakinada", "Kakinada", "Andhra Pradesh"),
    "534": ("Eluru", "West Godavari", "Andhra Pradesh"),
    "50": ("Telangana", "Telangana", "Telangana"),
    "51": ("Andhra Pradesh", "Andhra Pradesh", "Andhra Pradesh"),
    "52": ("Andhra Pradesh", "Andhra Pradesh", "Andhra Pradesh"),
    "53": ("Andhra Pradesh", "Andhra Pradesh", "Andhra Pradesh"),
    # Karnataka (56, 57, 58, 59)
    "560": ("Bengaluru", "Bengaluru Urban", "Karnataka"),
    "561": ("Doddaballapur", "Bengaluru Rural", "Karnataka"),
    "562": ("Ramanagara", "Ramanagara", "Karnataka"),
    "563": ("Kolar", "Kolar", "Karnataka"),
    "570": ("Mysuru", "Mysuru", "Karnataka"),
    "571": ("Mandya", "Mandya", "Karnataka"),
    "572": ("Tumakuru", "Tumakuru", "Karnataka"),
    "573": ("Hassan", "Hassan", "Karnataka"),
    "574": ("Udupi", "Udupi", "Karnataka"),
    "575": ("Mangaluru", "Dakshina Kannada", "Karnataka"),
    "577": ("Shivamogga", "Shivamogga", "Karnataka"),
    "580": ("Hubballi", "Dharwad", "Karnataka"),
    "581": ("Belagavi", "Belagavi", "Karnataka"),
    "583": ("Ballari", "Ballari", "Karnataka"),
    "584": ("Raichur", "Raichur", "Karnataka"),
    "585": ("Kalaburagi", "Kalaburagi", "Karnataka"),
    "586": ("Vijayapura", "Vijayapura", "Karnataka"),
    "590": ("Belagavi", "Belagavi", "Karnataka"),
    "56": ("Karnataka", "Karnataka", "Karnataka"),
    "57": ("Karnataka", "Karnataka", "Karnataka"),
    "58": ("Karnataka", "Karnataka", "Karnataka"),
    "59": ("Karnataka", "Karnataka", "Karnataka"),
    # Tamil Nadu & Puducherry (60, 61, 62, 63, 64)
    "600": ("Chennai", "Chennai", "Tamil Nadu"),
    "601": ("Tiruvallur", "Tiruvallur", "Tamil Nadu"),
    "602": ("Kanchipuram", "Kanchipuram", "Tamil Nadu"),
    "603": ("Chengalpattu", "Chengalpattu", "Tamil Nadu"),
    "605": ("Puducherry", "Puducherry", "Puducherry"),
    "611": ("Nagapattinam", "Nagapattinam", "Tamil Nadu"),
    "613": ("Thanjavur", "Thanjavur", "Tamil Nadu"),
    "620": ("Tiruchirappalli", "Tiruchirappalli", "Tamil Nadu"),
    "624": ("Dindigul", "Dindigul", "Tamil Nadu"),
    "625": ("Madurai", "Madurai", "Tamil Nadu"),
    "627": ("Tirunelveli", "Tirunelveli", "Tamil Nadu"),
    "628": ("Thoothukudi", "Thoothukudi", "Tamil Nadu"),
    "629": ("Nagercoil", "Kanyakumari", "Tamil Nadu"),
    "632": ("Vellore", "Vellore", "Tamil Nadu"),
    "635": ("Krishnagiri", "Krishnagiri", "Tamil Nadu"),
    "636": ("Salem", "Salem", "Tamil Nadu"),
    "638": ("Erode", "Erode", "Tamil Nadu"),
    "641": ("Coimbatore", "Coimbatore", "Tamil Nadu"),
    "642": ("Pollachi", "Coimbatore", "Tamil Nadu"),
    "643": ("Ooty", "Nilgiris", "Tamil Nadu"),
    "60": ("Tamil Nadu", "Tamil Nadu", "Tamil Nadu"),
    "61": ("Tamil Nadu", "Tamil Nadu", "Tamil Nadu"),
    "62": ("Tamil Nadu", "Tamil Nadu", "Tamil Nadu"),
    "63": ("Tamil Nadu", "Tamil Nadu", "Tamil Nadu"),
    "64": ("Tamil Nadu", "Tamil Nadu", "Tamil Nadu"),
    # Kerala & Lakshadweep (67, 68, 69)
    "670": ("Kannur", "Kannur", "Kerala"),
    "671": ("Kasaragod", "Kasaragod", "Kerala"),
    "673": ("Kozhikode", "Kozhikode", "Kerala"),
    "676": ("Malappuram", "Malappuram", "Kerala"),
    "678": ("Palakkad", "Palakkad", "Kerala"),
    "680": ("Thrissur", "Thrissur", "Kerala"),
    "682": ("Kochi", "Ernakulam", "Kerala"),
    "685": ("Idukki", "Idukki", "Kerala"),
    "686": ("Kottayam", "Kottayam", "Kerala"),
    "688": ("Alappuzha", "Alappuzha", "Kerala"),
    "689": ("Pathanamthitta", "Pathanamthitta", "Kerala"),
    "691": ("Kollam", "Kollam", "Kerala"),
    "695": ("Thiruvananthapuram", "Thiruvananthapuram", "Kerala"),
    "67": ("Kerala", "Kerala", "Kerala"),
    "68": ("Kerala", "Kerala", "Kerala"),
    "69": ("Kerala", "Kerala", "Kerala"),
    # West Bengal & Andaman (70, 71, 72, 73, 74)
    "700": ("Kolkata", "Kolkata", "West Bengal"),
    "711": ("Howrah", "Howrah", "West Bengal"),
    "712": ("Hooghly", "Hooghly", "West Bengal"),
    "713": ("Durgapur", "Paschim Bardhaman", "West Bengal"),
    "721": ("Kharagpur", "Paschim Medinipur", "West Bengal"),
    "734": ("Siliguri", "Darjeeling", "West Bengal"),
    "735": ("Jalpaiguri", "Jalpaiguri", "West Bengal"),
    "741": ("Nadia", "Nadia", "West Bengal"),
    "743": ("South 24 Parganas", "South 24 Parganas", "West Bengal"),
    "744": ("Port Blair", "Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
    "70": ("West Bengal", "West Bengal", "West Bengal"),
    "71": ("West Bengal", "West Bengal", "West Bengal"),
    "72": ("West Bengal", "West Bengal", "West Bengal"),
    "73": ("West Bengal", "West Bengal", "West Bengal"),
    "74": ("West Bengal", "West Bengal", "West Bengal"),
    # Odisha (75, 76, 77)
    "751": ("Bhubaneswar", "Khurda", "Odisha"),
    "752": ("Puri", "Puri", "Odisha"),
    "753": ("Cuttack", "Cuttack", "Odisha"),
    "756": ("Balasore", "Balasore", "Odisha"),
    "760": ("Berhampur", "Ganjam", "Odisha"),
    "768": ("Sambalpur", "Sambalpur", "Odisha"),
    "769": ("Rourkela", "Sundargarh", "Odisha"),
    "75": ("Odisha", "Odisha", "Odisha"),
    "76": ("Odisha", "Odisha", "Odisha"),
    "77": ("Odisha", "Odisha", "Odisha"),
    # Assam & North East (78, 79)
    "781": ("Guwahati", "Kamrup Metropolitan", "Assam"),
    "782": ("Nagaon", "Nagaon", "Assam"),
    "785": ("Jorhat", "Jorhat", "Assam"),
    "786": ("Dibrugarh", "Dibrugarh", "Assam"),
    "788": ("Silchar", "Cachar", "Assam"),
    "791": ("Itanagar", "Papum Pare", "Arunachal Pradesh"),
    "793": ("Shillong", "East Khasi Hills", "Meghalaya"),
    "795": ("Imphal", "Imphal West", "Manipur"),
    "796": ("Aizawl", "Aizawl", "Mizoram"),
    "797": ("Dimapur", "Dimapur", "Nagaland"),
    "799": ("Agartala", "West Tripura", "Tripura"),
    "737": ("Gangtok", "East Sikkim", "Sikkim"),
    "78": ("Assam", "Assam", "Assam"),
    "79": ("North East", "North East", "Assam"),
    # Bihar & Jharkhand (80, 81, 82, 83, 84, 85)
    "800": ("Patna", "Patna", "Bihar"),
    "801": ("Danapur", "Patna", "Bihar"),
    "802": ("Arrah", "Bhojpur", "Bihar"),
    "803": ("Bihar Sharif", "Nalanda", "Bihar"),
    "812": ("Bhagalpur", "Bhagalpur", "Bihar"),
    "814": ("Deoghar", "Deoghar", "Jharkhand"),
    "823": ("Gaya", "Gaya", "Bihar"),
    "824": ("Aurangabad", "Aurangabad", "Bihar"),
    "825": ("Hazaribagh", "Hazaribagh", "Jharkhand"),
    "826": ("Dhanbad", "Dhanbad", "Jharkhand"),
    "827": ("Bokaro", "Bokaro", "Jharkhand"),
    "831": ("Jamshedpur", "East Singhbhum", "Jharkhand"),
    "834": ("Ranchi", "Ranchi", "Jharkhand"),
    "841": ("Chhapra", "Saran", "Bihar"),
    "842": ("Muzaffarpur", "Muzaffarpur", "Bihar"),
    "843": ("Sitamarhi", "Sitamarhi", "Bihar"),
    "844": ("Hajipur", "Vaishali", "Bihar"),
    "845": ("Motihari", "East Champaran", "Bihar"),
    "846": ("Darbhanga", "Darbhanga", "Bihar"),
    "847": ("Madhubani", "Madhubani", "Bihar"),
    "848": ("Samastipur", "Samastipur", "Bihar"),
    "851": ("Begusarai", "Begusarai", "Bihar"),
    "852": ("Saharsa", "Saharsa", "Bihar"),
    "854": ("Purnia", "Purnia", "Bihar"),
    "80": ("Bihar", "Bihar", "Bihar"),
    "81": ("Bihar", "Bihar", "Bihar"),
    "82": ("Jharkhand", "Jharkhand", "Jharkhand"),
    "83": ("Jharkhand", "Jharkhand", "Jharkhand"),
    "84": ("Bihar", "Bihar", "Bihar"),
    "85": ("Bihar", "Bihar", "Bihar"),
}

# In-memory LRU / hash cache for pan-India PIN lookups
_PINCODE_PAN_INDIA_CACHE: Dict[str, Dict[str, Any]] = {}


def fetch_india_post_official(pin: str) -> Optional[Dict[str, Any]]:
    """
    Fetch exact locality, district, and state from official India Post directory for all 19,000+ PIN codes.
    """
    try:
        url = f"https://api.postalpincode.in/pincode/{pin}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (GenericMedsAI/1.0; Pan-India Pincode Directory)"}
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, list) and data[0].get("Status") == "Success":
                post_offices = data[0].get("PostOffice") or []
                if post_offices:
                    po = post_offices[0]
                    # Clean up city/block name
                    city_candidate = po.get("Block") or po.get("Name") or po.get("District")
                    if city_candidate and city_candidate.lower() in ("na", "n/a", "null"):
                        city_candidate = po.get("District")
                    district_name = po.get("District") or city_candidate or ""
                    state_name = po.get("State") or ""
                    return {
                        "pincode": pin,
                        "city": city_candidate or district_name,
                        "district": district_name,
                        "state": state_name,
                        "source": "india_post_official",
                        "found": True,
                    }
    except Exception:
        pass
    return None


def lookup_pincode(pincode: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Auto-detect city, district, and state from any 6-digit Indian PIN code across Pan-India.
    1. Checks in-memory cache for instant response.
    2. Checks verified JanAushadhiKendra database records.
    3. Fetches live from official India Post Pan-India API.
    4. Falls back to comprehensive Postal Circle and sub-district prefix mapping.
    """
    clean_pin = re.sub(r"\D", "", str(pincode or "")).strip()
    if not clean_pin or len(clean_pin) != 6 or not PINCODE_REGEX.match(clean_pin):
        return {
            "pincode": clean_pin,
            "city": "",
            "district": "",
            "state": "",
            "found": False,
            "message": "PIN code must be a 6-digit number starting with 1-9."
        }

    # 1. In-memory cache hit
    if clean_pin in _PINCODE_PAN_INDIA_CACHE:
        return _PINCODE_PAN_INDIA_CACHE[clean_pin]

    # 2. Exact DB match from JanAushadhiKendra
    if db:
        kendra = db.query(JanAushadhiKendra).filter(JanAushadhiKendra.pincode == clean_pin).first()
        if kendra:
            res = {
                "pincode": clean_pin,
                "city": kendra.city or kendra.district or "",
                "district": kendra.district or kendra.city or "",
                "state": kendra.state or "",
                "source": "verified_kendra_db",
                "found": True
            }
            _PINCODE_PAN_INDIA_CACHE[clean_pin] = res
            return res

    # 3. Live Official India Post API (covering all Pan-India postal codes)
    live_res = fetch_india_post_official(clean_pin)
    if live_res:
        _PINCODE_PAN_INDIA_CACHE[clean_pin] = live_res
        return live_res

    # 4. Fallback: match against prefix hierarchy (5, 4, 3, 2 digits)
    for length in (5, 4, 3, 2):
        prefix = clean_pin[:length]
        if prefix in POSTAL_PREFIX_MAP:
            city, district, state = POSTAL_PREFIX_MAP[prefix]
            fallback_res = {
                "pincode": clean_pin,
                "city": city,
                "district": district,
                "state": state,
                "source": "postal_circle_index",
                "found": True
            }
            _PINCODE_PAN_INDIA_CACHE[clean_pin] = fallback_res
            return fallback_res

    return {
        "pincode": clean_pin,
        "city": "",
        "district": "",
        "state": "",
        "found": False,
        "message": f"Could not determine locality for PIN {clean_pin}."
    }

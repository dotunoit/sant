from app import db
from models import Staff

staff_list = [
    {"id": 1, "name": "AISHAT ASELEBE", "phone": "07828437973"},
    {"id": 2, "name": "AMANDA BASS", "phone": "07840264775"},
    {"id": 3, "name": 'ASHVINI "ASH" DON', "phone": "07860822084"},
    {"id": 4, "name": "DAMI ORIMOOGUNJE", "phone": "07833834159"},
    {"id": 5, "name": "DAMILOLA ESTHER OWOFADEJU", "phone": "07393155176"},
    {"id": 6, "name": "DARRYL TAPFUMA", "phone": "07957549435"},
    {"id": 7, "name": 'DOTUN "ALEX" OMOBOYE', "phone": "07745991647"},
    {"id": 8, "name": 'ERANDI "ANDI" GUNASEKARA', "phone": "07838902789"},
    {"id": 9, "name": "FOZIA LUNBA", "phone": "07407121467"},
    {"id": 10, "name": 'IMMACULATE "MACU" DIMONYE', "phone": "07717596444"},
    {"id": 11, "name": "IRIN SHAJU", "phone": "07867087425"},
    {"id": 12, "name": "JOLE KAREN SAKEYU", "phone": "07778114791"},
    {"id": 13, "name": "KEVIN TIMSON", "phone": "07846199563"},
    {"id": 14, "name": "MADHU DON", "phone": "07309268918"},
    {"id": 15, "name": "M.A SAEED", "phone": "07424061472"},
    {"id": 16, "name": "MARIATOU JALLOW", "phone": "07392926381"},
    {"id": 17, "name": "MICHAEL ASELEBE", "phone": "07482113212"},
    {"id": 18, "name": 'OLAMIDE "OLA" SIMEON DAIRO', "phone": "07920698160"},
    {"id": 19, "name": 'OLUWADAMILARE "WALE" OLAWALE', "phone": "07823813330"},
    {"id": 20, "name": 'ONOME "MAVIS" ERTHLARHAGHEN', "phone": "07733790213"},
    {"id": 21, "name": "THILINI PANNILA", "phone": "07800534011"},
    {"id": 22, "name": "VISHAL ADAV", "phone": "07305192575"},
    {"id": 23, "name": 'VIVEKANANDA "VIVEK" SADHU', "phone": "07464843439"},
    {"id": 24, "name": "ZAINAB FALADE", "phone": "07789067252"},
]

for staff in staff_list:
    db.session.add(Staff(id=staff["id"], name=staff["name"], phone=staff["phone"]))

db.session.commit()
print("Staff table populated successfully!")

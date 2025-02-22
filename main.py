# main.py

from contextlib import asynccontextmanager
import uuid
from datetime import date, datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Date, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# DB konfiguratsiyasi – sinov uchun sqlite, real loyihalarda boshqa DB tavsiya etiladi
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# --- Asosiy Model: TimeStampedModel ---
class TimeStampedModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# --- Region Model ---
class Region(TimeStampedModel):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    districts = relationship("District", back_populates="region")

# --- District Model ---
class District(TimeStampedModel):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    region = relationship("Region", back_populates="districts")
    schools = relationship("School", back_populates="district")

# --- School Model ---
class School(TimeStampedModel):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    district = relationship("District", back_populates="schools")

# --- Librarian Model ---
class Librarian(TimeStampedModel):
    __tablename__ = "librarians"
    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String, nullable=True)  # fayl yoʻli sifatida
    ism = Column(String(255), nullable=False)
    familiya = Column(String(255), nullable=False)
    telefon_raqam = Column(String(13), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_premium_user = Column(Boolean, default=False)
    premium_ends = Column(DateTime, nullable=True)
    adress = Column(String(255), nullable=True)
    is_telegram_authenticated = Column(Boolean, default=False)
    telegram_user_id = Column(String(255), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    school = relationship("School")
    formulars = relationship("Formular", back_populates="librarian")

# --- Formular Model ---
class Formular(TimeStampedModel):
    __tablename__ = "formulars"
    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String, nullable=True)
    ism = Column(String(255), nullable=False)
    familiya = Column(String(255), nullable=False)
    otasining_ismi = Column(String(255), nullable=True)
    tugilgan_sanasi = Column(Date, nullable=False)
    uid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'oquvchi', 'oqituvchi', 'boshqa'
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    manzili = Column(String(255), nullable=False)
    telefon_raqam = Column(String(13), nullable=False)
    sinf = Column(Integer, nullable=True)
    sinf_type = Column(String(10), nullable=True)
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    librarian = relationship("Librarian", back_populates="formulars")
    transactions = relationship("BookTransaction", back_populates="formular")

# --- BookTransaction Model ---
class BookTransaction(TimeStampedModel):
    __tablename__ = "booktransactions"
    id = Column(Integer, primary_key=True, index=True)
    formular_id = Column(Integer, ForeignKey("formulars.id"), nullable=False)
    kitob_qaytarish_muddati = Column(Date, nullable=False)
    kitob_olingan_sana = Column(DateTime, default=func.now(), nullable=False)
    kitob_qaytarilgan_sana = Column(DateTime, nullable=True)
    inventar_raqami = Column(String(100), nullable=False)
    bolim = Column(String(100), nullable=False)
    muallif = Column(String(255), nullable=False)
    kitob_nomi = Column(String(255), nullable=False)
    is_returned = Column(Boolean, default=False)
    formular = relationship("Formular", back_populates="transactions")

# --- Pydantic Schemas ---
class RegionBase(BaseModel):
    name: str

class RegionCreate(RegionBase):
    pass

class RegionOut(RegionBase):
    id: int
    model_config = {"from_attributes": True}

class DistrictBase(BaseModel):
    name: str
    region_id: int

class DistrictCreate(DistrictBase):
    pass

class DistrictOut(DistrictBase):
    id: int
    model_config = {"from_attributes": True}

class SchoolBase(BaseModel):
    name: str
    district_id: int

class SchoolCreate(SchoolBase):
    pass

class SchoolOut(SchoolBase):
    id: int
    model_config = {"from_attributes": True}

class LibrarianBase(BaseModel):
    ism: str
    familiya: str
    telefon_raqam: str
    school_id: Optional[int] = None

class LibrarianCreate(LibrarianBase):
    pass

class LibrarianOut(LibrarianBase):
    id: int
    model_config = {"from_attributes": True}

class FormularBase(BaseModel):
    ism: str
    familiya: str
    tugilgan_sanasi: date
    role: str
    school_id: int
    manzili: str
    telefon_raqam: str
    librarian_id: int
    sinf: Optional[int] = None
    sinf_type: Optional[str] = None

class FormularCreate(FormularBase):
    pass

class FormularOut(FormularBase):
    id: int
    uid: str
    model_config = {"from_attributes": True}

class BookTransactionBase(BaseModel):
    formular_id: int
    kitob_qaytarish_muddati: date
    inventar_raqami: str
    bolim: str
    muallif: str
    kitob_nomi: str
    is_returned: bool

class BookTransactionCreate(BookTransactionBase):
    pass

class BookTransactionOut(BookTransactionBase):
    id: int
    kitob_olingan_sana: datetime
    kitob_qaytarilgan_sana: Optional[datetime] = None
    model_config = {"from_attributes": True}


# --- Ilova va CORS sozlamalari ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# DB session dependency
async def get_db():
    async with async_session() as session:
        yield session



#####

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy import text  # text() funksiyasini import qilamiz
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import asyncio

app = FastAPI()

# SQLAlchemy uchun asosiy sozlashlar
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Pydantic modellari
class RegionBase(BaseModel):
    name: str

class RegionCreate(RegionBase):
    pass

class RegionOut(RegionBase):
    id: int

class DistrictBase(BaseModel):
    name: str
    region_id: int

class DistrictCreate(DistrictBase):
    pass

class DistrictOut(DistrictBase):
    id: int

class SchoolBase(BaseModel):
    name: str
    district_id: int

class SchoolCreate(SchoolBase):
    pass

class SchoolOut(SchoolBase):
    id: int

class LibrarianBase(BaseModel):
    ism: str
    familiya: str
    telefon_raqam: str
    school_id: int

class LibrarianCreate(LibrarianBase):
    pass

class LibrarianOut(LibrarianBase):
    id: int

class FormularBase(BaseModel):
    ism: str
    familiya: str
    tugilgan_sanasi: date
    role: str
    school_id: int
    manzili: str
    telefon_raqam: str
    librarian_id: int
    sinf: Optional[int] = None
    sinf_type: Optional[str] = None

class FormularCreate(FormularBase):
    pass

class FormularOut(FormularBase):
    id: int

# Database sessionni olish uchun dependency
async def get_db():
    async with async_session() as session:
        yield session

# ============================================================================
# Regions Endpointlari
# ============================================================================
@app.get("/regions", response_model=List[RegionOut])
async def list_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM regions"))
    return result.fetchall()

@app.get("/regions/{region_id}", response_model=RegionOut)
async def get_region(region_id: int, db: AsyncSession = Depends(get_db)):
    region = await db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@app.post("/regions", response_model=RegionOut)
async def create_region(region: RegionCreate, db: AsyncSession = Depends(get_db)):
    db_region = Region(name=region.name)
    db.add(db_region)
    await db.commit()
    await db.refresh(db_region)
    return db_region

@app.put("/regions/{region_id}", response_model=RegionOut)
async def update_region(region_id: int, region: RegionCreate, db: AsyncSession = Depends(get_db)):
    db_region = await db.get(Region, region_id)
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")
    db_region.name = region.name
    await db.commit()
    await db.refresh(db_region)
    return db_region

@app.delete("/regions/{region_id}")
async def delete_region(region_id: int, db: AsyncSession = Depends(get_db)):
    db_region = await db.get(Region, region_id)
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")
    await db.delete(db_region)
    await db.commit()
    return {"detail": "Region deleted"}

# ============================================================================
# Districts Endpointlari
# ============================================================================
@app.get("/districts", response_model=List[DistrictOut])
async def list_districts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM districts"))
    return result.fetchall()

@app.get("/districts/{district_id}", response_model=DistrictOut)
async def get_district(district_id: int, db: AsyncSession = Depends(get_db)):
    district = await db.get(District, district_id)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    return district

@app.get("/regions/{region_id}/districts", response_model=List[DistrictOut])
async def get_districts_by_region(region_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM districts WHERE region_id = :region_id"),
        {"region_id": region_id}
    )
    return result.fetchall()

@app.post("/districts", response_model=DistrictOut)
async def create_district(district: DistrictCreate, db: AsyncSession = Depends(get_db)):
    db_district = District(name=district.name, region_id=district.region_id)
    db.add(db_district)
    await db.commit()
    await db.refresh(db_district)
    return db_district

@app.post("/regions/{region_id}/districts", response_model=DistrictOut)
async def create_district_in_region(region_id: int, district: DistrictCreate, db: AsyncSession = Depends(get_db)):
    db_district = District(name=district.name, region_id=region_id)
    db.add(db_district)
    await db.commit()
    await db.refresh(db_district)
    return db_district

@app.put("/districts/{district_id}", response_model=DistrictOut)
async def update_district(district_id: int, district: DistrictCreate, db: AsyncSession = Depends(get_db)):
    db_district = await db.get(District, district_id)
    if not db_district:
        raise HTTPException(status_code=404, detail="District not found")
    db_district.name = district.name
    db_district.region_id = district.region_id
    await db.commit()
    await db.refresh(db_district)
    return db_district

@app.delete("/districts/{district_id}")
async def delete_district(district_id: int, db: AsyncSession = Depends(get_db)):
    db_district = await db.get(District, district_id)
    if not db_district:
        raise HTTPException(status_code=404, detail="District not found")
    await db.delete(db_district)
    await db.commit()
    return {"detail": "District deleted"}

# ============================================================================
# Schools Endpointlari
# ============================================================================
@app.get("/schools", response_model=List[SchoolOut])
async def list_schools(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM schools"))
    return result.fetchall()

@app.get("/schools/{school_id}", response_model=SchoolOut)
async def get_school(school_id: int, db: AsyncSession = Depends(get_db)):
    school = await db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@app.get("/districts/{district_id}/schools", response_model=List[SchoolOut])
async def get_schools_by_district(district_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM schools WHERE district_id = :district_id"),
        {"district_id": district_id}
    )
    return result.fetchall()

@app.post("/schools", response_model=SchoolOut)
async def create_school(school: SchoolCreate, db: AsyncSession = Depends(get_db)):
    db_school = School(name=school.name, district_id=school.district_id)
    db.add(db_school)
    await db.commit()
    await db.refresh(db_school)
    return db_school

@app.post("/districts/{district_id}/schools", response_model=SchoolOut)
async def create_school_in_district(district_id: int, school: SchoolCreate, db: AsyncSession = Depends(get_db)):
    db_school = School(name=school.name, district_id=district_id)
    db.add(db_school)
    await db.commit()
    await db.refresh(db_school)
    return db_school

@app.put("/schools/{school_id}", response_model=SchoolOut)
async def update_school(school_id: int, school: SchoolCreate, db: AsyncSession = Depends(get_db)):
    db_school = await db.get(School, school_id)
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    db_school.name = school.name
    db_school.district_id = school.district_id
    await db.commit()
    await db.refresh(db_school)
    return db_school

@app.delete("/schools/{school_id}")
async def delete_school(school_id: int, db: AsyncSession = Depends(get_db)):
    db_school = await db.get(School, school_id)
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    await db.delete(db_school)
    await db.commit()
    return {"detail": "School deleted"}

# ============================================================================
# Librarians Endpointlari
# ============================================================================
@app.get("/librarians", response_model=List[LibrarianOut])
async def list_librarians(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM librarians"))
    return result.fetchall()

@app.get("/librarians/{librarian_id}", response_model=LibrarianOut)
async def get_librarian(librarian_id: int, db: AsyncSession = Depends(get_db)):
    librarian = await db.get(Librarian, librarian_id)
    if not librarian:
        raise HTTPException(status_code=404, detail="Librarian not found")
    return librarian

@app.get("/schools/{school_id}/librarians", response_model=List[LibrarianOut])
async def get_librarians_by_school(school_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM librarians WHERE school_id = :school_id"),
        {"school_id": school_id}
    )
    return result.fetchall()

@app.post("/librarians", response_model=LibrarianOut)
async def create_librarian(librarian: LibrarianCreate, db: AsyncSession = Depends(get_db)):
    db_librarian = Librarian(
        ism=librarian.ism,
        familiya=librarian.familiya,
        telefon_raqam=librarian.telefon_raqam,
        school_id=librarian.school_id
    )
    db.add(db_librarian)
    await db.commit()
    await db.refresh(db_librarian)
    return db_librarian

@app.post("/schools/{school_id}/librarians", response_model=LibrarianOut)
async def create_librarian_in_school(school_id: int, librarian: LibrarianCreate, db: AsyncSession = Depends(get_db)):
    db_librarian = Librarian(
        ism=librarian.ism,
        familiya=librarian.familiya,
        telefon_raqam=librarian.telefon_raqam,
        school_id=school_id
    )
    db.add(db_librarian)
    await db.commit()
    await db.refresh(db_librarian)
    return db_librarian

@app.put("/librarians/{librarian_id}", response_model=LibrarianOut)
async def update_librarian(librarian_id: int, librarian: LibrarianCreate, db: AsyncSession = Depends(get_db)):
    db_librarian = await db.get(Librarian, librarian_id)
    if not db_librarian:
        raise HTTPException(status_code=404, detail="Librarian not found")
    db_librarian.ism = librarian.ism
    db_librarian.familiya = librarian.familiya
    db_librarian.telefon_raqam = librarian.telefon_raqam
    db_librarian.school_id = librarian.school_id
    await db.commit()
    await db.refresh(db_librarian)
    return db_librarian

@app.delete("/librarians/{librarian_id}")
async def delete_librarian(librarian_id: int, db: AsyncSession = Depends(get_db)):
    db_librarian = await db.get(Librarian, librarian_id)
    if not db_librarian:
        raise HTTPException(status_code=404, detail="Librarian not found")
    await db.delete(db_librarian)
    await db.commit()
    return {"detail": "Librarian deleted"}

# ============================================================================
# Formulars Endpointlari
# ============================================================================
@app.get("/formulars", response_model=List[FormularOut])
async def list_formulars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM formulars"))
    return result.fetchall()

@app.get("/formulars/{formular_id}", response_model=FormularOut)
async def get_formular(formular_id: int, db: AsyncSession = Depends(get_db)):
    formular = await db.get(Formular, formular_id)
    if not formular:
        raise HTTPException(status_code=404, detail="Formular not found")
    return formular

@app.get("/librarians/{librarian_id}/formulars", response_model=List[FormularOut])
async def get_formulars_by_librarian(librarian_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM formulars WHERE librarian_id = :librarian_id"),
        {"librarian_id": librarian_id}
    )
    return result.fetchall()

@app.get("/schools/{school_id}/formulars",response_model=List[FormularOut])
async def get_formulars_by_school(school_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM formulars WHERE school_id = :school_id"),
        {"school_id": school_id}
    )
    return result.fetchall()

@app.post("/formulars", response_model=FormularOut)
async def create_formular(formular: FormularCreate, db: AsyncSession = Depends(get_db)):
    db_formular = Formular(
        ism=formular.ism,
        familiya=formular.familiya,
        tugilgan_sanasi=formular.tugilgan_sanasi,
        role=formular.role,
        school_id=formular.school_id,
        manzili=formular.manzili,
        telefon_raqam=formular.telefon_raqam,
        librarian_id=formular.librarian_id,
        sinf=formular.sinf,
        sinf_type=formular.sinf_type
    )
    db.add(db_formular)
    await db.commit()
    await db.refresh(db_formular)
    return db_formular

@app.post("/librarians/{librarian_id}/formulars", response_model=FormularOut)
async def create_formular_for_librarian(librarian_id: int, formular: FormularCreate, db: AsyncSession = Depends(get_db)):
    db_formular = Formular(
        ism=formular.ism,
        familiya=formular.familiya,
        tugilgan_sanasi=formular.tugilgan_sanasi,
        role=formular.role,
        school_id=formular.school_id,
        manzili=formular.manzili,
        telefon_raqam=formular.telefon_raqam,
        librarian_id=librarian_id,
        sinf=formular.sinf,
        sinf_type=formular.sinf_type
    )
    db.add(db_formular)
    await db.commit()
    await db.refresh(db_formular)
    return db_formular

@app.put("/formulars/{formular_id}", response_model=FormularOut)
async def update_formular(formular_id: int, formular: FormularCreate, db: AsyncSession = Depends(get_db)):
    db_formular = await db.get(Formular, formular_id)
    if not db_formular:
        raise HTTPException(status_code=404, detail="Formular not found")
    db_formular.ism = formular.ism
    db_formular.familiya = formular.familiya
    db_formular.tugilgan_sanasi = formular.tugilgan_sanasi
    db_formular.role = formular.role
    db_formular.school_id = formular.school_id
    db_formular.manzili = formular.manzili
    db_formular.telefon_raqam = formular.telefon_raqam
    db_formular.librarian_id = formular.librarian_id
    db_formular.sinf = formular.sinf
    db_formular.sinf_type = formular.sinf_type
    await db.commit()
    await db.refresh(db_formular)
    return db_formular

@app.delete("/formulars/{formular_id}")
async def delete_formular(formular_id: int, db: AsyncSession = Depends(get_db)):
    db_formular = await db.get(Formular, formular_id)
    if not db_formular:
        raise HTTPException(status_code=404, detail="Formular not found")
    await db.delete(db_formular)
    await db.commit()
    return {"detail": "Formular deleted"}

# ============================================================================
# Run the FastAPI app
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

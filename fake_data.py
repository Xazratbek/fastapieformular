import asyncio
from faker import Faker
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from main import Base, Region, District, School, Librarian, Formular, BookTransaction

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Initialize Faker
fake = Faker()

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Function to create fake regions
async def create_fake_regions():
    async with async_session() as session:
        regions = [Region(name=fake.unique.city()) for _ in range(12)]
        session.add_all(regions)
        await session.commit()
        print("Created 12 regions.")

# Function to create fake districts
async def create_fake_districts():
    async with async_session() as session:
        regions = (await session.execute(select(Region))).scalars().all()
        districts = []
        for region in regions:
            for _ in range(125):  # 125 districts per region (12 × 125 = 1500 districts)
                districts.append(District(name=fake.unique.city(), region_id=region.id))
        session.add_all(districts)
        await session.commit()
        print("Created 1500 districts.")

# Function to create fake schools
async def create_fake_schools():
    async with async_session() as session:
        districts = (await session.execute(select(District))).scalars().all()
        schools = [School(name=fake.unique.company(), district_id=district.id) for district in districts for _ in range(10)]  # 10 schools per district (1500 × 10 = 15000 schools)
        session.add_all(schools)
        await session.commit()
        print("Created 15000 schools.")

# Function to create fake librarians
async def create_fake_librarians():
    async with async_session() as session:
        schools = (await session.execute(select(School))).scalars().all()
        librarians = [Librarian(
            ism=fake.first_name(),
            familiya=fake.last_name(),
            telefon_raqam=fake.unique.phone_number(),
            school_id=school.id
        ) for school in schools]
        session.add_all(librarians)
        await session.commit()
        print("Created 15000 librarians.")

# Function to create fake formulars (students, teachers, others)
async def create_fake_formulars():
    async with async_session() as session:
        librarians = (await session.execute(select(Librarian))).scalars().all()
        formulars = []
        for librarian in librarians:
            # 10 students
            for _ in range(1):
                formulars.append(Formular(
                    ism=fake.first_name(),
                    familiya=fake.last_name(),
                    tugilgan_sanasi=fake.date_of_birth(minimum_age=6, maximum_age=18),
                    role="oquvchi",
                    school_id=librarian.school_id,
                    manzili=fake.address(),
                    telefon_raqam=fake.unique.phone_number(),
                    librarian_id=librarian.id,
                    sinf=fake.random_int(min=1, max=11),
                    sinf_type=fake.random_element(elements=("A", "B", "C"))
                ))
            # 10 teachers
            for _ in range(1):
                formulars.append(Formular(
                    ism=fake.first_name(),
                    familiya=fake.last_name(),
                    tugilgan_sanasi=fake.date_of_birth(minimum_age=25, maximum_age=65),
                    role="oqituvchi",
                    school_id=librarian.school_id,
                    manzili=fake.address(),
                    telefon_raqam=fake.unique.phone_number(),
                    librarian_id=librarian.id
                ))
            # 10 others
            for _ in range(1):
                formulars.append(Formular(
                    ism=fake.first_name(),
                    familiya=fake.last_name(),
                    tugilgan_sanasi=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    role="boshqa",
                    school_id=librarian.school_id,
                    manzili=fake.address(),
                    telefon_raqam=fake.unique.phone_number(),
                    librarian_id=librarian.id
                ))
        session.add_all(formulars)
        await session.commit()
        print("Created formulars (students, teachers, others).")

# Function to create fake book transactions
async def create_fake_book_transactions():
    async with async_session() as session:
        formulars = (await session.execute(select(Formular))).scalars().all()
        transactions = []
        for formular in formulars:
            # 10 returned transactions
            for _ in range(10):
                transactions.append(BookTransaction(
                    formular_id=formular.id,
                    kitob_qaytarish_muddati=fake.future_date(end_date="+30d"),
                    inventar_raqami=fake.unique.uuid4(),
                    bolim=fake.word(),
                    muallif=fake.name(),
                    kitob_nomi=fake.catch_phrase(),
                    is_returned=True,
                    kitob_qaytarilgan_sana=fake.past_date(start_date="-30d")
                ))
            # 1 not returned transaction
            transactions.append(BookTransaction(
                formular_id=formular.id,
                kitob_qaytarish_muddati=fake.future_date(end_date="+30d"),
                inventar_raqami=fake.unique.uuid4(),
                bolim=fake.word(),
                muallif=fake.name(),
                kitob_nomi=fake.catch_phrase(),
                is_returned=False
            ))
        session.add_all(transactions)
        await session.commit()
        print("Created book transactions.")

# Main function to generate all fake data
async def main():
    await create_fake_regions()
    await create_fake_districts()
    await create_fake_schools()
    await create_fake_librarians()
    await create_fake_formulars()
    await create_fake_book_transactions()

# Run the script
if __name__ == "__main__":
    asyncio.run(main())

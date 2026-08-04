import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_operario_or_admin
from app.core.database import get_db
from app.models.animal import Animal
from app.schemas.animal import AnimalCreate, AnimalOut

router = APIRouter(prefix="/animals", tags=["animals"])


@router.get(
    "",
    response_model=list[AnimalOut],
    description="Busca animales por caravana, usado para el autocompletado de la madre",
    dependencies=[Depends(get_current_user)],
)
def search_animals(search: str = "", limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Animal)
    if search:
        query = query.filter(Animal.caravana.ilike(f"%{search}%"))
    return query.order_by(Animal.caravana).limit(limit).all()


@router.post(
    "",
    response_model=AnimalOut,
    status_code=status.HTTP_201_CREATED,
    description="Alta manual de un animal (madre)",
    dependencies=[Depends(require_operario_or_admin)],
)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db)):
    if db.query(Animal).filter(Animal.caravana == payload.caravana).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un animal con esa caravana")

    animal = Animal(caravana=payload.caravana, sexo=payload.sexo, estado=payload.estado)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


@router.post(
    "/import-csv",
    description="Importa animales desde un CSV con columnas: caravana,sexo,estado. Filas con caravana ya existente se omiten.",
    dependencies=[Depends(require_operario_or_admin)],
)
async def import_animals_csv(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    existing = {a.caravana for a in db.query(Animal.caravana).all()}
    created = 0
    skipped = 0

    for row in reader:
        caravana = (row.get("caravana") or "").strip()
        if not caravana or caravana in existing:
            skipped += 1
            continue

        estado_raw = (row.get("estado") or "true").strip().lower()
        animal = Animal(
            caravana=caravana,
            sexo=(row.get("sexo") or "").strip(),
            estado=estado_raw in ("1", "true", "activo", "si", "sí"),
        )
        db.add(animal)
        existing.add(caravana)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}

# User (schema "public", tabla de tambo) deliberadamente NO se exporta acá
# — se importa directo como `from app.models.user import User` donde hace
# falta, para que alembic/env.py (que importa desde este paquete) nunca la
# vea y nunca intente migrarla. Ver también app/models/user.py.
from app.models.foto_referencia import FotoReferencia
from app.models.resultado import ResultadoLaboratorio
from app.models.tipo_analisis import TipoAnalisis

__all__ = ["FotoReferencia", "ResultadoLaboratorio", "TipoAnalisis"]

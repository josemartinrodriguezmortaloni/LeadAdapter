# Lead Adapter
Lead adapter va a ser una API Rest que utiliza agentes de inteligencia artificial para generar mensajes personalizados, evitando patrones de spam y adaptándose al contexto del lead, el emisor y el playbook comercial. Para el funcionamiento óptimo de la API, el sistema recibirá de su parte datos estructurados de los leads, información del remitente y el playbook.

A partir de estos datos, la solución ejecuta una pipeline secuencial de IA que realiza las siguientes funciones:
- Análisis de contexto: Evaluación profunda de la información del cliente potencial y el perfil del emisor.
- Generación de contenido personalizado: Creación de mensajes adaptados a las necesidades específicas de cada interacción.
- Optimización de secuencias: Producción de una serie de mensajes optimizados para objetivos de ventas o marketing.

# Tech Stack
Voy a estar usando el siguiente stack tecnológico:
- Framework principal: FastAPI
- Para validación de información: Pydantic 
- LLM: OpenAI gpt-5-mini y gpt-5.1
- Testing: pytest

# Resumen de lo realizado

Hasta la actualidad se ha realizado la fase 0 y fase 1. En la fase 0 se creó la estructura de carpetas src/ siguiendo la arquitectura hexagonal (domain, application, infrastructure, api), se generaron todos los archivos __init__.py para que Python reconozca los paquetes, se configuró el pyproject.toml con las dependencias del proyecto (FastAPI, Pydantic, OpenAI, pytest, ruff, etc.) y el requirements.txt para ambientes que no usen uv, y se creó el .env.example como plantilla de variables de entorno (API keys, configuración).

En la fase 1, se implementó toda la capa de dominio, la cual tiene la siguiente escrutura:
```markdown
src/domain/
├── entities/           # Objetos de negocio mutables con identidad
│   ├── lead.py         # Core: La persona a contactar
│   ├── message.py      # Output: Mensaje generado
│   ├── playbook.py     # Config: Playbook de ventas
│   └── sender.py       # Contexto: Quién envía el mensaje
│
├── value_objects/      # Objetos inmutables sin identidad
│   ├── campaign_history.py   # Historial de contacto del lead
│   ├── icp_profile.py        # Perfil de Cliente Ideal
│   ├── product.py            # Producto que se vende
│   └── work_experience.py    # Historial laboral del lead
│
├── enums/              # Constantes type-safe
│   ├── channel.py          # LINKEDIN | EMAIL
│   ├── message_strategy.py # TECHNICAL_PEER | BUSINESS_VALUE | ...
│   ├── seniority.py        # C_LEVEL | VP | DIRECTOR | ...
│   └── sequence_step.py    # FIRST_CONTACT | FOLLOW_UP_1 | ...
│
├── services/           # Servicios de dominio (lógica stateless)
│   ├── icp_matcher.py       # Matchea leads con ICPs
│   ├── seniority_inferrer.py # Infiere seniority desde job title
│   └── strategy_selector.py  # Selecciona estrategia de mensaje
│
└── exceptions/         # Errores específicos del dominio
    └── domain_exceptions.py  # Jerarquía de excepciones estructuradas
```
La capa de dominio representa la **lógica de negocio central** de LeadAdapter, un sistema para generar mensajes personalizados de outreach para leads de ventas. Esta capa es:

- **Agnóstica de frameworks**: Sin dependencias de FastAPI, bases de datos o servicios externos
- **Python puro**: Usa solo biblioteca estándar + dataclasses
- **Alineada con DDD**: Sigue los principios de Domain-Driven De

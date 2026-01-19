# Lead Adapter
Lead adapter va a ser una API Rest que utiliza agentes de inteligencia artificial para generar mensajes personalizados, evitando patrones de spam y adaptándose al contexto del lead, el emisor y el playbook comercial. Para el funcionamiento óptimo de la API, el sistema recibirá de su parte datos estructurados de los leads, información del remitente y el playbook.

# Feature
A partir de estos datos, la solución ejecuta una pipeline secuencial de IA que realiza las siguientes funciones:
- Análisis de contexto: Evaluación profunda de la información del cliente potencial y el perfil del emisor.
- Generación de contenido personalizado: Creación de mensajes adaptados a las necesidades específicas de cada interacción.
- Optimización de secuencias: Producción de una serie de mensajes optimizados para objetivos de ventas o marketing.

# Quick Start
## Clonar e instalar
```bash
git clone https://github.com/tu-usuario/leadadapter.git
cd leadadapter
uv sync  # o: pip install -r requirements.txt
```

## Configurar

`cp .env.example .env`

## Editar .env con tu OPENAI_API_KEY

Agregar tu api key a la variable

`OPENAI_API_KEY=YOUR_API_KEY`

## Correr

`uv run uvicorn src.main:app --reload`

# Tech Stack

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI |
| Validación | Pydantic v2 |
| LLM | OpenAI GPT-4o-mini |
| Testing | pytest |
| Linting | ruff |


# Decisiones de Diseño

## ¿Por qué Arquitectura Hexagonal?

- **Desacoplamiento**: La lógica de negocio no depende de frameworks ni detalles de infraestructura
- **Testabilidad**: El dominio se puede testear sin mocks de APIs externas
- **Flexibilidad**: Permite cambiar OpenAI por otro LLM sin tocar el dominio

## ¿Por qué DDD (Domain-Driven Design)?

- **Complejidad del problema**: Leads, ICPs, estrategias y scoring requieren un modelo rico
- **Lenguaje ubicuo**: Las entidades reflejan conceptos de negocio (Lead, Playbook, Sender)
- **Encapsulación**: Las reglas de negocio viven dentro de las entidades (`__post_init__`)

## Patrones Aplicados

| Patrón | Dónde | Justificación |
|--------|-------|---------------|
| **Value Object** | `Product`, `ICPProfile`, `WorkExperience` | Inmutabilidad, igualdad por valor |
| **Entity** | `Lead`, `Message`, `Playbook`, `Sender` | Identidad + ciclo de vida |
| **Domain Service** | `ICPMatcher`, `SeniorityInferrer`, `StrategySelector` | Lógica stateless que no pertenece a una entidad |
| **Self-Validation** | Todas las entidades (`__post_init__`) | Objetos siempre válidos (fail-fast) |
| **Strategy** | `MessageStrategy` enum | Estrategias de mensaje intercambiables |
| **Template Method** | `DomainException.to_problem_detail()` | Comportamiento base + customización |

---

# Resumen de lo Realizado

| Fase | Estado | Descripción |
|------|--------|-------------|
| 0 - Setup | Completada | Estructura hexagonal, configuración |
| 1 - Domain | Completada | Entidades, VOs, Servicios de dominio |
| 2 - Application | En progreso | Use Cases, DTOs, Ports |
| 3 - Infrastructure | Pendiente | Adapters, OpenAI, Cache |
| 4 - API | Pendiente | Endpoints, middleware |


## Fase 0 - Setup del Proyecto

**Objetivo**: Establecer la estructura base del proyecto siguiendo arquitectura hexagonal.

**Entregables**:
- Estructura de carpetas `src/` con arquitectura hexagonal
  - `domain/` - Lógica de negocio pura
  - `application/` - Casos de uso y orquestación
  - `infrastructure/` - Adaptadores externos (OpenAI, cache)
  - `api/` - Endpoints REST
- Archivos `__init__.py` para reconocimiento de paquetes Python
- `pyproject.toml` con dependencias (FastAPI, Pydantic, OpenAI, pytest, ruff)
- `requirements.txt` para ambientes sin `uv`
- `.env.example` como plantilla de variables de entorno

## Fase 1 - Capa de Dominio

**Objetivo**: Implementar la lógica de negocio central siguiendo DDD, sin dependencias externas.

**Entregables**:
- **4 Entidades**: `Lead`, `Message`, `Playbook`, `Sender`
- **4 Value Objects**: `WorkExperience`, `CampaignHistory`, `Product`, `ICPProfile`
- **4 Enums**: `Channel`, `Seniority`, `MessageStrategy`, `SequenceStep`
- **3 Servicios de Dominio**: `ICPMatcher`, `SeniorityInferrer`, `StrategySelector`
- **10 Excepciones**: Jerarquía estructurada compatible con RFC 7807
- **Validación en construcción**: Todas las entidades validan en `__post_init__`
- **100% Python puro**: Sin dependencias de frameworks

### Estructura de la Capa

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
- **Alineada con DDD**: Sigue los principios de Domain-Driven Design

### Modelo de Dominio Completo

```mermaid
classDiagram
    direction TB
    
    %% ===== ENTIDADES =====
    class Lead {
        +str first_name
        +str job_title
        +str company_name
        +str? last_name
        +list~WorkExperience~ work_experience
        +CampaignHistory? campaign_history
        +str? bio
        +list~str~ skills
        +str? linkedin_url
        --
        +full_name: str
        +years_in_current_role() int?
        +has_previous_contact() bool
    }
    
    class Message {
        +str content
        +Channel channel
        +SequenceStep sequence_step
        +MessageStrategy strategy_used
        +float quality_score
        +str message_id
        +dict quality_breakdown
        +int tokens_used
        +int generation_time_ms
        +datetime created_at
        --
        +word_count: int
        +char_count: int
        +passes_quality_gate(threshold) bool
    }
    
    class Playbook {
        +str communication_style
        +list~Product~ products
        +list~ICPProfile~ icp_profiles
        +list~str~ success_cases
        +list~str~ common_objections
        +list~str~ value_propositions
        --
        +get_product_for_icp(icp) Product?
    }
    
    class Sender {
        +str name
        +str company_name
        +str? job_title
        +str? email
        --
        +signature: str
    }
    
    %% ===== VALUE OBJECTS =====
    class WorkExperience {
        <<frozen>>
        +str company
        +str title
        +date start_date
        +date? end_date
        +str? description
        --
        +is_current: bool
        +duration_years() int
        +duration_months() int
    }
    
    class CampaignHistory {
        <<frozen>>
        +int total_attempts
        +datetime? last_contact_date
        +str? last_channel
        +int responses_received
        +str? last_response_sentiment
        --
        +has_responded: bool
        +response_rate: float
        +days_since_last_contact() int?
    }
    
    class Product {
        <<frozen>>
        +str name
        +str description
        +list~str~ key_benefits
        +list~str~ target_problems
        +list~str~ differentiators
        --
        +get_benefit_for_pain(pain) str?
    }
    
    class ICPProfile {
        <<frozen>>
        +str name
        +list~str~ target_titles
        +list~str~ target_industries
        +tuple~int,int~ company_size_range
        +list~str~ pain_points
        +list~str~ keywords_sector
        --
        +matches_title(job_title) bool
        +get_relevant_pain_points(seniority) list~str~
    }
    
    %% ===== ENUMS =====
    class Channel {
        <<enumeration>>
        LINKEDIN
        EMAIL
        --
        +max_length: int
        +requires_subject: bool
    }
    
    class Seniority {
        <<enumeration>>
        C_LEVEL
        VP
        DIRECTOR
        MANAGER
        SENIOR
        MID
        JUNIOR
        UNKNOWN
        --
        +is_decision_maker: bool
        +is_technical: bool
    }
    
    class MessageStrategy {
        <<enumeration>>
        TECHNICAL_PEER
        BUSINESS_VALUE
        PROBLEM_SOLUTION
        SOCIAL_PROOF
        CURIOSITY_HOOK
        MUTUAL_CONNECTION
        --
        +description: str
        +for_seniority(str) list
    }
    
    class SequenceStep {
        <<enumeration>>
        FIRST_CONTACT
        FOLLOW_UP_1
        FOLLOW_UP_2
        BREAKUP
        --
        +message_tone: str
        +urgency_level: int
    }
    
    %% ===== SERVICIOS DE DOMINIO =====
    class ICPMatcher {
        +match(lead, playbook) ICPProfile?
        -_calculate_match_score(lead, icp) float
    }
    
    class SeniorityInferrer {
        +PATTERNS: list~tuple~
        +infer(job_title) Seniority
    }
    
    class StrategySelector {
        +select(lead, channel, step, playbook, seniority) MessageStrategy
    }
    
    %% ===== RELACIONES DE ENTIDADES =====
    Lead "1" *-- "0..*" WorkExperience : contiene
    Lead "1" *-- "0..1" CampaignHistory : tiene
    
    Playbook "1" *-- "1..*" Product : contiene
    Playbook "1" *-- "0..*" ICPProfile : contiene
    
    Message --> Channel : usa
    Message --> SequenceStep : usa
    Message --> MessageStrategy : usa
    
    ICPProfile --> Seniority : usa para filtrar
    
    %% ===== RELACIONES DE SERVICIOS DE DOMINIO =====
    ICPMatcher --> Lead : matchea
    ICPMatcher --> Playbook : usa
    ICPMatcher --> ICPProfile : retorna
    
    SeniorityInferrer --> Seniority : retorna
    
    StrategySelector --> Lead : analiza
    StrategySelector --> Playbook : usa
    StrategySelector --> MessageStrategy : retorna
```

### Diagrama de secuencias

#### Secuencia 1: Flujo de Procesamiento de Lead 

```mermaid
sequenceDiagram
    autonumber
    participant Cliente
    participant UseCase as GenerateMessageUseCase
    participant SI as SeniorityInferrer
    participant IM as ICPMatcher
    participant SS as StrategySelector
    participant Lead
    participant Playbook
    
    Cliente->>UseCase: generate(lead_dto, playbook_dto)
    
    rect rgb(240, 248, 255)
        Note over UseCase,Lead: 1. Creación y Validación de Entidad
        UseCase->>Lead: create(first_name, job_title, ...)
        Lead-->>Lead: validación __post_init__
        alt Validación falla
            Lead-->>UseCase: raise InvalidLeadError
        end
    end
    
    rect rgb(255, 248, 240)
        Note over UseCase,SI: 2. Inferencia de Seniority
        UseCase->>SI: infer(lead.job_title)
        SI-->>SI: Matchear patrones (CEO→C_LEVEL, etc.)
        SI-->>UseCase: Seniority.SENIOR
    end
    
    rect rgb(240, 255, 240)
        Note over UseCase,IM: 3. Matching de ICP
        UseCase->>IM: match(lead, playbook)
        loop Por cada ICP en playbook
            IM-->>IM: calculate_match_score()
        end
        alt Score >= 0.3
            IM-->>UseCase: mejor_icp_matcheado
        else Sin match
            IM-->>UseCase: None
        end
    end
    
    rect rgb(255, 240, 255)
        Note over UseCase,SS: 4. Selección de Estrategia
        UseCase->>SS: select(lead, channel, step, playbook, seniority)
        SS-->>SS: Verificar contacto previo
        SS-->>SS: Verificar paso de secuencia
        SS-->>SS: Aplicar mapeo de seniority
        SS-->>UseCase: MessageStrategy.TECHNICAL_PEER
    end
    
    UseCase-->>Cliente: Contexto listo para LLM
```

#### Secuencia 2: Flujo de Validación de Entidad

```mermaid
sequenceDiagram
    autonumber
    participant Codigo as Código Cliente
    participant Lead
    participant VE as ValidationException
    participant Handler as Error Handler
    
    Codigo->>Lead: Lead(first_name="", job_title="Dev", ...)
    Lead->>Lead: __post_init__()
    Lead->>Lead: verificar first_name.strip()
    
    alt first_name está vacío
        Lead->>VE: raise InvalidLeadError(field="first_name", reason="cannot be empty")
        VE-->>VE: Setear HTTP_STATUS=422
        VE-->>VE: Setear instance_id, timestamp
        VE-->>Codigo: Excepción se propaga
        
        Codigo->>Handler: catch InvalidLeadError
        Handler->>VE: e.to_problem_detail()
        VE-->>Handler: dict RFC 7807
        Handler-->>Codigo: JSONResponse (422)
    else first_name es válido
        Lead-->>Codigo: Instancia de Lead creada
    end
```

#### Secuencia 3: Algoritmo de Matching de ICP

```mermaid
sequenceDiagram
    autonumber
    participant Llamador
    participant IM as ICPMatcher
    participant ICP1 as ICP: "Tech Leaders"
    participant ICP2 as ICP: "Developers"
    participant Lead
    
    Llamador->>IM: match(lead, playbook)
    
    Note over IM: Inicializar best_score=0, best_match=None
    
    rect rgb(240, 248, 255)
        Note over IM,ICP1: Evaluar ICP 1
        IM->>IM: _calculate_match_score(lead, icp1)
        IM->>Lead: leer job_title="Senior Developer"
        IM->>ICP1: leer target_titles=["CTO", "Director"]
        Note over IM: title_matches = 0
        IM->>ICP1: leer keywords_sector=["leadership"]
        Note over IM: keyword_matches = 0
        Note over IM: Score = 0.0
    end
    
    rect rgb(255, 248, 240)
        Note over IM,ICP2: Evaluar ICP 2
        IM->>IM: _calculate_match_score(lead, icp2)
        IM->>Lead: leer job_title="Senior Developer"
        IM->>ICP2: leer target_titles=["developer", "engineer"]
        Note over IM: title_matches = 1 (developer)
        Note over IM: title_score = 0.5 * (1/2) = 0.25
        IM->>ICP2: leer keywords_sector=["python", "aws"]
        Note over IM: keyword_matches = 0
        IM->>Lead: leer skills=["python", "docker"]
        Note over IM: skills_matches = 1 (python)
        Note over IM: skills_score = 0.2 * (1/2) = 0.1
        Note over IM: Score Total = 0.35
    end
    
    Note over IM: Mejor: ICP2 con score 0.35 >= 0.3
    IM-->>Llamador: return ICP: "Developers"
```

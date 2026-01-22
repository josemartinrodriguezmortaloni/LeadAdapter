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

---

# Resumen de lo Realizado

| Fase | Estado | Descripción |
|------|--------|-------------|
| 0 - Setup | Completada | Estructura hexagonal, configuración |
| 1 - Domain | Completada | Entidades, VOs, Servicios de dominio |
| 2 - Application | Completada | Use Cases, DTOs, Ports, Services |
| 3 - Infrastructure | Completada | Adapters, OpenAI, Cache, Prompts |
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

## Fase 2 - Capa de Aplicación

**Objetivo**: Implementar la lógica de orquestación siguiendo Arquitectura Hexagonal con Ports & Adapters, conectando el dominio con la infraestructura a través de abstracciones.

**Entregables**:
- **2 Puertos (Interfaces)**: `LLMPort`, `CachePort`
- **6 DTOs de Request**: `LeadDTO`, `SenderDTO`, `PlaybookDTO`, `WorkExperienceDTO`, `CampaignHistoryDTO`, `ICPProfileDTO`, `ProductDTO`, `GenerateMessageRequest`
- **5 DTOs de Response**: `GenerateMessageResponse`, `QualityDTO`, `QualityBreakdownDTO`, `MetadataDTO`, `ErrorResponse`, `HealthResponse`
- **1 Use Case**: `GenerateMessageUseCase`
- **4 Application Services**: `PromptChainOrchestrator`, `MessageScorer`, `QualityGate`, `EntityMapper`
- **5 Scoring Criteria (Strategy)**: `ScoringCriterion` (ABC), `PersonalizationCriterion`, `AntiSpamCriterion`, `StructureCriterion`, `ToneCriterion`

### Estructura de la Capa

```
src/application/
├── ports/                  # Interfaces (contratos para infraestructura)
│   ├── llm_port.py         # Puerto para LLMs (complete, complete_json, count_tokens)
│   └── cache_port.py       # Puerto para cache (get, set, delete, exists, get_or_set)
│
├── dtos/                   # Data Transfer Objects (Pydantic)
│   ├── requests.py         # DTOs de entrada: Lead, Sender, Playbook, Request
│   └── responses.py        # DTOs de salida: Response, Quality, Metadata, Error
│
├── use_cases/              # Casos de uso (orquestación principal)
│   └── generate_message.py # GenerateMessageUseCase: coordina todo el flujo
│
├── services/               # Servicios de aplicación
│   ├── prompt_chain_orchestrator.py  # Cadena de 3 prompts LLM
│   ├── quality_gate.py               # Control de calidad con reintentos
│   ├── message_scorer.py             # Scorer extensible (Strategy Pattern)
│   └── scoring/                      # Criterios de scoring pluggables
│       ├── scoring_criterion.py      # ABC para criterios
│       ├── personalization_criterion.py
│       ├── anti_spam_criterion.py
│       ├── structure_criterion.py
│       └── tone_criterion.py
│
└── mappers/                # Conversión DTO ↔ Entidad
    └── entity_mapper.py    # Data Mapper Pattern
```

La capa de aplicación representa la **orquestación y coordinación** entre el dominio y la infraestructura. Esta capa:

- **Depende solo de abstracciones**: Los puertos son interfaces ABC que la infraestructura implementa
- **Usa Pydantic para validación**: DTOs validan datos de entrada/salida automáticamente
- **Implementa Cache-Aside**: Verifica cache antes de procesar, guarda resultados exitosos
- **Extensible via Strategy**: Nuevos criterios de scoring sin modificar código existente

### Modelo de la Capa de Aplicación

```mermaid
classDiagram
    direction TB
    
    %% ===== PUERTOS (INTERFACES) =====
    class LLMPort {
        <<interface>>
        +complete(prompt, system_prompt, temperature, max_output_tokens) LLMResponse
        +complete_json(prompt, system_prompt, temperature) LLMResponse
        +count_tokens(text) int
    }
    
    class LLMResponse {
        <<frozen>>
        +str content
        +int prompt_tokens
        +int response_tokens
        +str model
        --
        +total_tokens: int
    }
    
    class CachePort {
        <<interface>>
        +get(key) Any?
        +set(key, value, ttl_seconds) None
        +delete(key) None
        +exists(key) bool
        +get_or_set(key, factory, ttl_seconds) Any
    }
    
    %% ===== DTOs REQUEST =====
    class GenerateMessageRequest {
        +str channel
        +str sequence_step
        +LeadDTO lead
        +SenderDTO sender
        +PlaybookDTO playbook
    }
    
    class LeadDTO {
        +str first_name
        +str? last_name
        +str job_title
        +str company_name
        +list~WorkExperienceDTO~ work_experience
        +CampaignHistoryDTO? campaign_history
        +str? bio
        +list~str~ skills
        +str? linkedin_url
    }
    
    class PlaybookDTO {
        +str communication_style
        +list~ProductDTO~ products
        +list~ICPProfileDTO~ icp_profiles
        +list~str~ success_cases
        +list~str~ value_propositions
    }
    
    %% ===== DTOs RESPONSE =====
    class GenerateMessageResponse {
        +str message_id
        +str content
        +QualityDTO quality
        +str strategy_used
        +MetadataDTO metadata
        +datetime created_at
    }
    
    class QualityDTO {
        +float score
        +QualityBreakdownDTO breakdown
        +bool passes_threshold
    }
    
    class MetadataDTO {
        +int tokens_used
        +int generation_time_ms
        +str model_used
        +int attempts
    }
    
    %% ===== USE CASE =====
    class GenerateMessageUseCase {
        +LLMPort llm
        +CachePort cache
        +PromptChainOrchestrator prompt_orchestrator
        +QualityGate quality_gate
        +StrategySelector strategy_selector
        +SeniorityInferrer seniority_inferrer
        +ICPMatcher icp_matcher
        +EntityMapper entity_mapper
        --
        +execute(request) GenerateMessageResponse
        -_build_cache_key(request) str
    }
    
    %% ===== APPLICATION SERVICES =====
    class PromptChainOrchestrator {
        +LLMPort llm
        --
        +execute_chain(lead, sender, ...) tuple~str,int~
        -_classify_lead(lead) tuple~LeadClassification,int~
        -_infer_context(lead, ...) tuple~InferredContext,int~
        -_generate_message(lead, ...) tuple~str,int~
    }
    
    class LeadClassification {
        +str role_type
        +float confidence
    }
    
    class InferredContext {
        +list~str~ pain_points
        +list~str~ hooks
        +list~str~ talking_points
    }
    
    class QualityGate {
        +PromptChainOrchestrator orchestrator
        +MessageScorer scorer
        +float threshold
        +int max_attempts
        --
        +generate_with_retry(lead, ...) tuple~Message,int~
    }
    
    class MessageScorer {
        -list~ScoringCriterion~ _criteria
        +STANDARD_CRITERIA: frozenset
        --
        +score(content, lead) ScoreBreakdown
        +get_criterion(name) ScoringCriterion?
        +max_possible_score: float
        +criteria: list
    }
    
    class ScoreBreakdown {
        +float personalization
        +float anti_spam
        +float structure
        +float tone
        +dict extra_scores
        --
        +total: float
        +get_score(name) float
        +to_dict() dict
    }
    
    %% ===== SCORING CRITERIA (STRATEGY) =====
    class ScoringCriterion {
        <<abstract>>
        +name: str
        +max_score: float
        --
        +score(content, lead) float
    }
    
    class PersonalizationCriterion {
        +name = "personalization"
        +max_score = 3.0
    }
    
    class AntiSpamCriterion {
        +name = "anti_spam"
        +max_score = 3.0
    }
    
    class StructureCriterion {
        +name = "structure"
        +max_score = 2.0
    }
    
    class ToneCriterion {
        +name = "tone"
        +max_score = 2.0
    }
    
    %% ===== MAPPER =====
    class EntityMapper {
        +to_lead(dto) Lead
        +to_sender(dto) Sender
        +to_playbook(dto) Playbook
    }
    
    %% ===== RELACIONES =====
    LLMPort ..> LLMResponse : returns
    
    GenerateMessageUseCase --> LLMPort : usa
    GenerateMessageUseCase --> CachePort : usa
    GenerateMessageUseCase --> PromptChainOrchestrator
    GenerateMessageUseCase --> QualityGate
    GenerateMessageUseCase --> EntityMapper
    GenerateMessageUseCase ..> GenerateMessageRequest : input
    GenerateMessageUseCase ..> GenerateMessageResponse : output
    
    PromptChainOrchestrator --> LLMPort : usa
    PromptChainOrchestrator ..> LeadClassification
    PromptChainOrchestrator ..> InferredContext
    
    QualityGate --> PromptChainOrchestrator
    QualityGate --> MessageScorer
    
    MessageScorer --> ScoringCriterion : strategy
    MessageScorer ..> ScoreBreakdown : returns
    
    ScoringCriterion <|-- PersonalizationCriterion
    ScoringCriterion <|-- AntiSpamCriterion
    ScoringCriterion <|-- StructureCriterion
    ScoringCriterion <|-- ToneCriterion
    
    GenerateMessageResponse --> QualityDTO
    GenerateMessageResponse --> MetadataDTO
    QualityDTO --> QualityBreakdownDTO
    
    GenerateMessageRequest --> LeadDTO
    GenerateMessageRequest --> PlaybookDTO
    
    EntityMapper ..> LeadDTO : maps from
    EntityMapper ..> Lead : maps to
```

### Diagrama de Secuencia: Flujo Completo del Use Case

```mermaid
sequenceDiagram
    autonumber
    participant API
    participant UC as GenerateMessageUseCase
    participant Cache as CachePort
    participant Mapper as EntityMapper
    participant SI as SeniorityInferrer
    participant IM as ICPMatcher
    participant SS as StrategySelector
    participant QG as QualityGate
    participant PCO as PromptChainOrchestrator
    participant Scorer as MessageScorer
    participant LLM as LLMPort
    
    API->>UC: execute(request)
    
    rect rgb(240, 248, 255)
        Note over UC,Cache: 1. Cache-Aside Check
        UC->>UC: _build_cache_key(request)
        UC->>Cache: get(cache_key)
        alt Cache Hit
            Cache-->>UC: cached_response
            UC-->>API: GenerateMessageResponse
        end
    end
    
    rect rgb(255, 248, 240)
        Note over UC,Mapper: 2. DTO → Domain Mapping
        UC->>Mapper: to_lead(request.lead)
        UC->>Mapper: to_sender(request.sender)
        UC->>Mapper: to_playbook(request.playbook)
    end
    
    rect rgb(240, 255, 240)
        Note over UC,SS: 3. Domain Services
        UC->>SI: infer(lead.job_title)
        SI-->>UC: Seniority.SENIOR
        UC->>IM: match(lead, playbook)
        IM-->>UC: matched_icp | None
        UC->>SS: select(lead, channel, ...)
        SS-->>UC: MessageStrategy
    end
    
    rect rgb(255, 240, 255)
        Note over QG,LLM: 4. Quality Gate con Retry
        UC->>QG: generate_with_retry(...)
        
        loop max_attempts (hasta pasar threshold)
            QG->>PCO: execute_chain(...)
            
            Note over PCO,LLM: Cadena de 3 prompts
            PCO->>LLM: complete_json (classify_lead)
            LLM-->>PCO: LeadClassification
            PCO->>LLM: complete_json (infer_context)
            LLM-->>PCO: InferredContext
            PCO->>LLM: complete (generate_message)
            LLM-->>PCO: message_content
            
            PCO-->>QG: (content, tokens)
            
            QG->>Scorer: score(content, lead)
            Scorer-->>QG: ScoreBreakdown
            
            alt score >= threshold
                QG-->>UC: (Message, attempts)
            else score < threshold
                Note over QG: Retry con nuevo intento
            end
        end
    end
    
    rect rgb(248, 255, 248)
        Note over UC,Cache: 5. Cache & Response
        UC->>UC: build GenerateMessageResponse
        UC->>Cache: set(cache_key, response, ttl)
        UC-->>API: GenerateMessageResponse
    end
```

## Fase 3 - Capa de Infraestructura

**Objetivo**: Implementar los adaptadores concretos que satisfacen los puertos definidos en Application Layer, conectando con servicios externos (OpenAI, Redis/Memory).

**Entregables**:
- **2 Adapters**: `OpenAIAdapter` (LLMPort), `MemoryCacheAdapter` (CachePort)
- **1 Configuración**: `Settings` (pydantic-settings con 12 variables)
- **3 Templates de Prompts**: `classify_lead`, `infer_context`, `generate_message`
- **Patrones Aplicados**: Adapter, Singleton (cached settings)

### Estructura de la Capa

```
src/infrastructure/
├── config/                 # Configuración de la aplicación
│   └── settings.py         # Settings con pydantic-settings (Singleton via lru_cache)
│
├── adapters/               # Implementaciones concretas de los puertos
│   ├── openai_adapter.py   # Implementa LLMPort → OpenAI API
│   └── memory_cache_adapter.py  # Implementa CachePort → Dict in-memory
│
└── prompts/                # Templates de prompts para LLM
    ├── classify_lead.py    # Prompt para clasificar rol del lead
    ├── infer_context.py    # Prompt para inferir pain points y hooks
    └── generate_message.py # Prompt para generar mensaje final
```

La capa de infraestructura representa los **detalles técnicos y conexiones externas**. Esta capa:

- **Implementa los puertos**: Los adapters son clases concretas que satisfacen las interfaces ABC
- **Es intercambiable**: Se puede cambiar OpenAI por Anthropic, o Memory por Redis, sin tocar Application
- **Centraliza configuración**: Settings usa pydantic-settings con variables de entorno
- **Encapsula prompts**: Los templates de prompts viven en infraestructura, no en dominio

### Modelo de la Capa de Infraestructura

```mermaid
classDiagram
    direction TB
    
    %% ===== PUERTOS (de Application) =====
    class LLMPort {
        <<interface>>
        +complete(prompt, system_prompt, temperature, max_output_tokens) LLMResponse
        +complete_json(prompt, system_prompt, temperature) LLMResponse
        +count_tokens(text) int
    }
    
    class CachePort {
        <<interface>>
        +get(key) Any?
        +set(key, value, ttl_seconds) None
        +delete(key) None
        +exists(key) bool
    }
    
    %% ===== ADAPTERS =====
    class OpenAIAdapter {
        -AsyncOpenAI client
        -str model
        -Settings settings
        -Encoding _encoding
        --
        +complete(prompt, ...) LLMResponse
        +complete_json(prompt, ...) LLMResponse
        +count_tokens(text) int
    }
    
    class MemoryCacheAdapter {
        -dict~str,CacheEntry~ _cache
        -asyncio.Lock _lock
        --
        +get(key) Any?
        +set(key, value, ttl_seconds) None
        +delete(key) None
        +exists(key) bool
        +clear() None
    }
    
    class CacheEntry {
        <<dataclass>>
        +Any value
        +datetime expires_at
    }
    
    %% ===== CONFIGURACIÓN =====
    class Settings {
        <<BaseSettings>>
        +str app_name
        +str app_version
        +bool debug
        --
        +str openai_api_key
        +str openai_model
        +int openai_timeout
        --
        +str? redis_url
        +int cache_ttl_seconds
        --
        +float quality_threshold
        +int max_generation_attempts
        --
        +int rate_limit_requests
        +int rate_limit_window_seconds
    }
    
    %% ===== PROMPTS =====
    class ClassifyLeadPrompt {
        <<module>>
        +CLASSIFY_LEAD_SYSTEM: str
        +build_classify_lead_prompt(job_title, company, seniority) str
    }
    
    class InferContextPrompt {
        <<module>>
        +INFER_CONTEXT_SYSTEM: str
        +build_infer_context_prompt(job_title, company, industry, ...) str
    }
    
    class GenerateMessagePrompt {
        <<module>>
        +GENERATE_MESSAGE_SYSTEM: str
        +build_generate_message_prompt(lead_name, ..., channel, strategy, ...) str
    }
    
    %% ===== RELACIONES =====
    LLMPort <|.. OpenAIAdapter : implements
    CachePort <|.. MemoryCacheAdapter : implements
    
    OpenAIAdapter --> Settings : usa
    MemoryCacheAdapter --> CacheEntry : almacena
    
    OpenAIAdapter ..> ClassifyLeadPrompt : usa
    OpenAIAdapter ..> InferContextPrompt : usa
    OpenAIAdapter ..> GenerateMessagePrompt : usa
```

### Tabla de Configuración (Settings)

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `app_name` | `str` | `"LeadAdapter"` | Nombre de la aplicación |
| `app_version` | `str` | `"1.0.0"` | Versión de la API |
| `debug` | `bool` | `False` | Modo debug |
| `openai_api_key` | `str` | **Required** | API Key de OpenAI |
| `openai_model` | `str` | `"gpt-5.1"` | Modelo a usar |
| `openai_timeout` | `int` | `30` | Timeout en segundos |
| `redis_url` | `str?` | `None` | URL de Redis (opcional) |
| `cache_ttl_seconds` | `int` | `3600` | TTL del cache (1 hora) |
| `quality_threshold` | `float` | `6.0` | Umbral de calidad (0-10) |
| `max_generation_attempts` | `int` | `3` | Intentos máximos |
| `rate_limit_requests` | `int` | `100` | Requests por ventana |
| `rate_limit_window_seconds` | `int` | `60` | Ventana de rate limit |

### Estructura de Prompts

| Prompt | System Prompt | User Prompt Builder | Output |
|--------|---------------|---------------------|--------|
| **classify_lead** | Clasificador B2B con 4 role types | `build_classify_lead_prompt(job_title, company, seniority)` | JSON: `{role_type, confidence, reasoning}` |
| **infer_context** | Experto en research B2B | `build_infer_context_prompt(job_title, company, industry, role_type, ...)` | JSON: `{pain_points[], hooks[], talking_points[]}` |
| **generate_message** | Copywriter B2B experto | `build_generate_message_prompt(lead_name, channel, strategy, pain_points, ...)` | String: mensaje final |

### Diagrama de Secuencia: Adapter Flow

```mermaid
sequenceDiagram
    autonumber
    participant PCO as PromptChainOrchestrator
    participant Adapter as OpenAIAdapter
    participant Prompts as Prompt Templates
    participant OpenAI as OpenAI API
    participant TikToken as tiktoken
    
    Note over PCO,OpenAI: Step 1: Classify Lead
    PCO->>Prompts: build_classify_lead_prompt(...)
    Prompts-->>PCO: user_prompt
    PCO->>Adapter: complete_json(prompt, CLASSIFY_LEAD_SYSTEM)
    Adapter->>OpenAI: responses.create(model, input, instructions, format=json)
    OpenAI-->>Adapter: Response{output_text, usage}
    Adapter-->>PCO: LLMResponse{content, tokens}
    
    Note over PCO,OpenAI: Step 2: Infer Context
    PCO->>Prompts: build_infer_context_prompt(...)
    Prompts-->>PCO: user_prompt
    PCO->>Adapter: complete_json(prompt, INFER_CONTEXT_SYSTEM)
    Adapter->>OpenAI: responses.create(...)
    OpenAI-->>Adapter: Response
    Adapter-->>PCO: LLMResponse
    
    Note over PCO,OpenAI: Step 3: Generate Message
    PCO->>Prompts: build_generate_message_prompt(...)
    Prompts-->>PCO: user_prompt
    PCO->>Adapter: complete(prompt, GENERATE_MESSAGE_SYSTEM)
    Adapter->>OpenAI: responses.create(...)
    OpenAI-->>Adapter: Response
    Adapter-->>PCO: LLMResponse
    
    Note over PCO,TikToken: Token Counting (anytime)
    PCO->>Adapter: count_tokens(text)
    Adapter->>TikToken: encode(text)
    TikToken-->>Adapter: token_list
    Adapter-->>PCO: len(tokens)
```


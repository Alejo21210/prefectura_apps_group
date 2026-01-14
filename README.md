# prefectura-eps

**Sistema de Cajas de Ahorro de la Economía Popular y Solidaria (EPS)**  
**GAD Prefectura de Pichincha – Proyecto MERA**

---

## 📌 Descripción general

Este repositorio contiene el desarrollo del **Módulo de Cajas de Ahorro EPS**, implementado sobre **Odoo 19**, destinado a la gestión integral de las Cajas de Ahorro de la Economía Popular y Solidaria de la Prefectura de Pichincha.

El sistema reemplaza los procesos manuales basados en Excel, incorporando una plataforma **segura, auditable, multi-caja y parametrizable**, alineada a los reglamentos internos de cada caja y a los Términos de Referencia (TDR) del proyecto.

📄 Documentación base del proyecto:
- Plan de Trabajo
- Propuesta Técnica
- Toma de Requisitos Funcionales
- Backlog e Issues de Desarrollo

---

## 🎯 Objetivo del sistema

Construir un sistema que permita:

- Gestionar **múltiples cajas de ahorro** con reglas propias.
- Registrar **socios, aportes, créditos, ingresos y egresos**.
- Controlar **cartera, mora y riesgo**.
- Generar **estados financieros, reportes e indicadores sociales**.
- Proveer **dashboards ejecutivos** para toma de decisiones.
- Garantizar **trazabilidad contable, auditoría y cumplimiento normativo**.

---

## 🧠 Enfoque funcional y técnico

### Arquitectura adoptada

El sistema sigue una **arquitectura híbrida EPS + Contabilidad**:

- **Dominio EPS (módulos propios)**  
  Modela la lógica real de operación de las Cajas de Ahorro (socios, aportes, créditos, reglas sociales).

- **Módulo `account` de Odoo**  
  Se utiliza exclusivamente como **motor contable y de auditoría** (asientos, balances, P&G).

> ⚠️ El sistema **NO replica una contabilidad empresarial tradicional**, sino que respeta la lógica real utilizada por las Cajas EPS, integrándose con `account` solo donde aporta valor.

---

## 🧩 Módulos funcionales (M01 – M12)

| Código | Módulo |
|------|-------|
| M01 | Cajas (multi-caja, parametrización, seguridad) |
| M02 | Socias y Socios |
| M03 | Registro de aportes |
| M04 | Libro diario de ingresos |
| M05 | Consolidado de ingresos |
| M06 | Control de cartera y créditos |
| M07 | Libro diario de egresos |
| M08 | Consolidado de egresos |
| M09 | Saldos |
| M10 | Estado de Pérdidas y Ganancias |
| M11 | Resumen financiero + indicadores sociales |
| M12 | Reportes e impresión |

---

## 🧱 ISSUES — Modelo de capas

| Nº ISSUE | Nombre del ISSUE | Capa principal | Rol en el sistema | Notas clave |
|--------|-----------------|---------------|------------------|------------|
| **ISSUE 00** | CAJAS EPS (multi-caja + roles + parámetros) | Infraestructura EPS | Base estructural | Define aislamiento, reglas y seguridad. Bloquea todo lo demás. |
| **ISSUE 01** | Listado Socios + indicadores sociales | Dominio EPS (Social) | Datos maestros | Núcleo social del sistema. No depende de la contabilidad. |
| **ISSUE 02** | Registro de Aportes + capital + arrastre | Operación EPS | Capitalización | Alimenta crédito, liquidaciones y patrimonio. |
| **ISSUE 03** | Libro diario de ingresos | Operación EPS | Operación diaria | Genera movimientos EPS y asientos contables. |
| **ISSUE 04** | Libro diario de egresos | Operación EPS | Operación diaria | Incluye desembolsos y gastos. |
| **ISSUE 05** | Cartera / Créditos / cuotas / vencida | Operación EPS (Riesgo) | Núcleo financiero EPS | Corazón del sistema. Controla riesgo y mora. |
| **ISSUE 06** | Integración contable EPS – Account | Infraestructura contable | Motor contable | Define reglas de generación de asientos. |
| **ISSUE 07** | PUC / códigos contables y mapeo | Infraestructura contable | Codificación | Permite auditoría y estados financieros correctos. |
| **ISSUE 08** | Estado P y G mensuales | Contabilidad | Resultado económico | Calcula excedente desde account. No es reporte EPS. |
| **ISSUE 09** | Balance general mensual | Contabilidad | Situación patrimonial | Valida ecuación contable. Insumo para cierres. |
| **ISSUE 10** | Liquidaciones / cierre anual | Contabilidad | Cierre y distribución | Usa P&G y capital. No recalcula operación. |
| **ISSUE 11** | REPORTES EPS (consolidados y resúmenes) | Reportes EPS | Consulta y presentación | Consume resultados, no calcula. Solo lectura. |
| **ISSUE 12** | Dashboard + alertas | Analítica / Control | Supervisión | KPIs y alertas. Capa ejecutiva. |
| **ISSUE 13** | Importación / migración + piloto | Soporte al despliegue | Validación real | No agrega lógica nueva. Prueba el sistema. |
| **ISSUE 14** | Manuales + capacitación + soporte | Cierre del proyecto | Transferencia | Asegura adopción y sostenibilidad. |

---

## 🏗️ Addons Odoo propuestos

Estructura modular del proyecto:

eps_cajas
eps_socios
eps_aportes
eps_creditos
eps_libros
eps_reportes
eps_dashboard

### Dependencias Odoo reutilizadas

- `base`
- `contacts`
- `account`
- `mail` (chatter / auditoría)

---

## 🔐 Roles y seguridad

El sistema implementa **control de accesos por rol y por caja**, incluyendo:

- Admin TI (Prefectura)
- Técnico macro / soporte
- Presidente/a
- Tesorero/a
- Secretario/a
- Socio/a (opcional – fase futura)

Cada usuario solo puede **ver y operar las cajas asignadas**, garantizando aislamiento de datos.

---

## 📊 Dashboards e indicadores

- **Indicadores financieros**:
  - liquidez
  - cartera
  - mora
  - excedentes

- **Indicadores sociales**:
  - género
  - tercera edad
  - discapacidad
  - edad promedio

- **Alertas de riesgo**:
  - pagos reiterados solo de intereses
  - créditos fuera de parámetros
  - concentración atípica de capital
  - garantes sobre comprometidos

---

## 🔄 Metodología de trabajo

- Desarrollo iterativo por fases
- Issues y backlog estructurados por capas
- Pruebas continuas
- Piloto en 2 cajas reales
- Retroalimentación y ajustes
- Capacitación certificada y transferencia de conocimiento

📆 Duración estimada del proyecto: **6 meses + 1 semana**

---

## 📦 Entregables

- Código fuente completo
- Manual técnico
- Manual de usuario
- Guía de instalación y configuración
- Capacitación (4 horas, con certificación)
- Informe final del proyecto

---

## 🛠️ Tecnologías

- **Odoo 19**
- Python
- PostgreSQL
- XML / QWeb (reportes)
- XLSX / CSV (importación y exportación)

---

## 📄 Licencia y uso

Repositorio **privado**, de uso exclusivo para el  
**GAD Prefectura de Pichincha / Proyecto MERA**.


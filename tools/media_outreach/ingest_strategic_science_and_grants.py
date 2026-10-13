"""
POLYDIM Strategic Science, National Grants & Global Governance Ingestion
Ingests US, EU, Asian, Spanish, and UN (ONU) strategic grants, academic awards, and leadership into SQLite databases.
"""

import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from outreach_db import init_db, upsert_contact
from strategic_grants_schema import apply_grants_schema

STRATEGIC_GRANTS_DATA = [
    # --- USA (DARPA & NSF) ---
    {
        "program_name": "DARPA HyDREA (Hyperdimensional Computing)",
        "agency": "DARPA / JUMP CRISP",
        "region": "US",
        "principal_investigator": "Prof. Tajana Rosing",
        "institution": "UC San Diego (SEELab)",
        "grant_code": "SRC GRC Task 2988.001 / JUMP CRISP",
        "topic_thrust": "HDC",
        "budget_range": "$5M - $15M Multi-Year",
        "summary": "Hyperdimensional computing system that is Robust, Efficient, and Accurate for RF classification and non-von Neumann tensor processing."
    },
    {
        "program_name": "DARPA SDH (Software-Defined Hardware)",
        "agency": "DARPA ERI",
        "region": "US",
        "principal_investigator": "Various ERI Consortium Leads",
        "institution": "DARPA Electronics Resurgence Initiative",
        "grant_code": "DARPA-BAA-HR001117S0056",
        "topic_thrust": "TENSOR_COMPILERS",
        "budget_range": "$75M Multi-Program",
        "summary": "Real-time reconfigurable hardware achieving ASIC performance efficiency with general-purpose software programmability for tensors."
    },
    {
        "program_name": "NSF CAREER: Decentralized Manifold Optimization",
        "agency": "NSF",
        "region": "US",
        "principal_investigator": "Prof. Shahin Shahrampour",
        "institution": "Northeastern University",
        "grant_code": "NSF-2203741 / NSF-2410328",
        "topic_thrust": "GEOMETRIC_AI",
        "budget_range": "$500K - $1M",
        "summary": "Foundations of scalable, fast, and online decentralized Riemannian manifold optimization in multi-agent networks."
    },

    # --- EUROPE & GERMANY (ERC & BMBF) ---
    {
        "program_name": "ERC Consolidator Grant: LEMAN",
        "agency": "European Research Council (ERC)",
        "region": "EU",
        "principal_investigator": "Prof. Michael Bronstein",
        "institution": "University of Oxford / Imperial College London",
        "grant_code": "ERC Grant No. 724228",
        "topic_thrust": "GEOMETRIC_AI",
        "budget_range": "€2.0M",
        "summary": "Deep LEarning on MANifolds and graphs (LEMAN). Foundational framework formalizing Geometric Deep Learning and symmetry equivariance."
    },
    {
        "program_name": "BMBF NEUROTEC: Memristive Neuromorphic Silicon",
        "agency": "BMBF (Germany)",
        "region": "DE",
        "principal_investigator": "Forschungszentrum Jülich / RWTH Aachen",
        "institution": "FZ Jülich / RWTH Aachen",
        "grant_code": "FKZ: 16ES1134 / 16ES1133K",
        "topic_thrust": "NEUROMORPHIC",
        "budget_range": "€36M",
        "summary": "Hardware-software co-design for energy-efficient analogue memristive cells and in-memory tensor processing."
    },
    {
        "program_name": "Horizon Europe: NEQIOS & NeuroSoC",
        "agency": "European Innovation Council (EIC Pathfinder)",
        "region": "EU",
        "principal_investigator": "EIC Consortia",
        "institution": "Horizon Europe Research Network",
        "grant_code": "Grant No. 101120237 / 101120763",
        "topic_thrust": "PIM",
        "budget_range": "€12M Consortia",
        "summary": "Analogue in-memory computing (AIMC) and phase change memory multiprocessor SoCs for ultra-fast edge inference."
    },

    # --- SPAIN (BSC, ICMAT, IMSE, PERTE CHIP) ---
    {
        "program_name": "European Processor Initiative (EPI) - RISC-V Vector Accelerators",
        "agency": "European Commission / PERTE Chip España",
        "region": "ES",
        "principal_investigator": "Prof. Mateo Valero",
        "institution": "Barcelona Supercomputing Center (BSC-CNS)",
        "grant_code": "EPI SGA2 / PRTR PERTE-CHIP",
        "topic_thrust": "TENSOR_COMPILERS",
        "budget_range": "€140M+ Multi-Partner",
        "summary": "Development of sovereign European RISC-V vector accelerators and tensor pipelines integrated into MareNostrum 5."
    },
    {
        "program_name": "PERTE Chip & Red Española de Supercomputación (RES)",
        "agency": "Agencia Estatal de Investigación (AEI) / MINECO",
        "region": "ES",
        "principal_investigator": "RES ICTS Governing Board",
        "institution": "Red Española de Supercomputación (RES) / BSC",
        "grant_code": "ICTS-RES-2024-PRTR",
        "topic_thrust": "PIM",
        "budget_range": "€60M+",
        "summary": "Strategic funding for microelectronics design, RISC-V high-performance vector computing, and national HPC sovereignty."
    },
    {
        "program_name": "Neuromorphic SNN & Event-Driven Vision (IMSE)",
        "agency": "Agencia Estatal de Investigación (AEI) / CSIC",
        "region": "ES",
        "principal_investigator": "Prof. Bernabé Linares-Barranco & Teresa Serrano-Gotarredona",
        "institution": "IMSE-CNM (CSIC / Universidad de Sevilla)",
        "grant_code": "AEI-PID-NEUROMORPHIC",
        "topic_thrust": "NEUROMORPHIC",
        "budget_range": "€2.5M",
        "summary": "Memristor-CMOS integration, Spike-Timing-Dependent Plasticity (STDP), and Address Event Representation (AER) chips."
    },

    # --- ASIA (CHINA, JAPAN, SOUTH KOREA) ---
    {
        "program_name": "NSFC Major Project: Integrated Photonic Tensor Cores",
        "agency": "NSFC (China)",
        "region": "CN",
        "principal_investigator": "Prof. Dai Qionghai",
        "institution": "Tsinghua University",
        "grant_code": "NSFC-Key-62088102",
        "topic_thrust": "PIM",
        "budget_range": "¥30M RMB",
        "summary": "Large-scale optical neural networks and photonic tensor cores performing high-dimensional continuous state transitions."
    },
    {
        "program_name": "JST Moonshot Goal 6: Information Geometry & Fault-Tolerant AI",
        "agency": "JST / NEDO (Japan)",
        "region": "JP",
        "principal_investigator": "Prof. Toru Aonishi & Prof. Masato Koashi",
        "institution": "The University of Tokyo",
        "grant_code": "JST Moonshot JPMJMS24A3",
        "topic_thrust": "GEOMETRIC_AI",
        "budget_range": "¥1.2B JPY",
        "summary": "Application of Information Geometry to non-linear physical systems, photonic interconnects, and non-tokenized continuous state spaces."
    },
    {
        "program_name": "MSIT Next-Gen PIM AI Semiconductor / PICORE Center",
        "agency": "MSIT / IITP (South Korea)",
        "region": "KR",
        "principal_investigator": "Prof. Kyoungsik Yu",
        "institution": "KAIST (PICORE Center)",
        "grant_code": "IITP-PIM-2024-001",
        "topic_thrust": "PIM",
        "budget_range": "₩25B KRW",
        "summary": "Integrated photonics and Processing-In-Memory (PIM) array accelerators for ultra-high throughput tensor processing."
    }
]

UN_GOVERNANCE_NODES = [
    {
        "full_name": "Independent International Scientific Panel on AI",
        "native_name": "UN International Scientific Panel on AI",
        "region": "GLOBAL",
        "organization": "United Nations (UN General Assembly A/RES/79/325)",
        "role_title": "Independent Global Scientific Body (40 Scientists, modeled after IPCC)",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#UN_AI, #ScientificConsensus, #GlobalGovernance, #OpenScience",
        "notes": "Co-chaired by Yoshua Bengio & Maria Ressa. Mandate to provide objective scientific assessment of AI capabilities, risks, and open foundational architecture."
    },
    {
        "full_name": "Amandeep Singh Gill",
        "native_name": "Amandeep Singh Gill",
        "region": "GLOBAL",
        "organization": "United Nations (Office of the Secretary-General's Envoy on Technology / UN-ODET)",
        "role_title": "Under-Secretary-General & Special Envoy for Digital and Emerging Tech",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#GlobalDigitalCompact, #UNTechEnvoy, #AIGovernance",
        "notes": "Leads the UN strategy on the Global Digital Compact, scientific AI dialogue, and open digital public goods."
    },
    {
        "full_name": "Carme Artigas",
        "native_name": "Carme Artigas",
        "region": "ES",
        "organization": "United Nations High-Level Advisory Body on AI (HLAB-AI)",
        "role_title": "Co-Chair of UN HLAB-AI / Former State Secretary of Digitalization Spain",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#UN_HLAB_AI, #GoverningAIforHumanity, #SpainAI",
        "notes": "Co-Chair of UN HLAB-AI delivering the 'Governing AI for Humanity' landmark roadmap for international AI infrastructure."
    },
    {
        "full_name": "ITU AI for Good Global Commission",
        "native_name": "ITU AI for Good",
        "region": "GLOBAL",
        "organization": "International Telecommunication Union (ITU - Geneva)",
        "role_title": "Specialized UN Agency for ICTs & Autonomous Standards",
        "tier": "PEER_RESEARCHER",
        "domain_tags": "#ITU, #AutonomousSystems, #AIStandards",
        "notes": "Global UN framework establishing technical and communication standards for AI autonomous systems and network protocols."
    }
]

def run_strategic_sync():
    init_db()
    apply_grants_schema()

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "POLYDIM_OUTREACH.sqlite")
    
    # 1. Ingest Strategic Grants
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM strategic_grants;")
    for g in STRATEGIC_GRANTS_DATA:
        cur.execute("""
        INSERT INTO strategic_grants (program_name, agency, region, principal_investigator, institution, grant_code, topic_thrust, budget_range, summary)
        VALUES (:program_name, :agency, :region, :principal_investigator, :institution, :grant_code, :topic_thrust, :budget_range, :summary)
        """, g)
    conn.commit()
    conn.close()

    # 2. Ingest UN Governance Nodes into contacts
    for node in UN_GOVERNANCE_NODES:
        upsert_contact(node)

    # 3. Ingest into POLYDIM_VECDB.sqlite facts
    vecdb_path = r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite"
    if os.path.exists(vecdb_path):
        vconn = sqlite3.connect(vecdb_path)
        vcur = vconn.cursor()
        for g in STRATEGIC_GRANTS_DATA:
            detail = f"Grant/Program: {g['program_name']} ({g['agency']}, {g['region']}). PI: {g['principal_investigator']} at {g['institution']}. Thrust: {g['topic_thrust']}. Summary: {g['summary']}"
            vcur.execute("""
            INSERT INTO facts (fact_type, source_file, version, topic, metric_key, metric_val, metric_unit, detail, certified, inserted_at)
            VALUES ('STRATEGIC_GOV_GRANT', 'STRATEGIC_GRANTS_PIPELINE', 'V1550', :topic, :name, :code, 'GRANT', :detail, 1, CURRENT_TIMESTAMP)
            """, {
                "topic": g["topic_thrust"],
                "name": g["program_name"],
                "code": g["grant_code"] or "N/A",
                "detail": detail
            })
        vconn.commit()
        vconn.close()

    print("✅ Successfully ingested all Strategic Grants, Spain & UN AI Leadership nodes (Exit Code 0).")

if __name__ == "__main__":
    run_strategic_sync()

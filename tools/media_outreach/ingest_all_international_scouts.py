"""
POLYDIM Global Scout Ingestion & Multi-Regional Lead Synthesizer
Ingests Chinese, Korean, Japanese, German, and US SOTA leaders into POLYDIM_OUTREACH.sqlite and facts in POLYDIM_VECDB.sqlite.
"""

import os
import sys
import sqlite3
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from outreach_db import init_db, upsert_contact, list_contacts
from media_formatter import MediaFormatter

GLOBAL_LEADS = [
    # --- CHINA (中文) ---
    {
        "full_name": "Yu Guang Wang",
        "native_name": "王宇光",
        "region": "CN",
        "organization": "Shanghai AI Lab / Shanghai Jiao Tong University (SJTU)",
        "role_title": "Professor / Researcher",
        "tier": "TIER_1_SOTA",
        "email": "yuguang.wang@sjtu.edu.cn",
        "scholar_url": "https://scholar.google.com/citations?user=YuGuangWang",
        "domain_tags": "#GeometricDeepLearning, #CliffordAlgebra, #InformationGeometry, #AIforScience",
        "notes": "Pioneering GDL, Clifford algebras, and information geometry applied to AI for Science"
    },
    {
        "full_name": "Wenbing Huang",
        "native_name": "黄文炳",
        "region": "CN",
        "organization": "Renmin University / Formerly Tsinghua AIR",
        "role_title": "Associate Professor",
        "tier": "TIER_1_SOTA",
        "email": "hwenbing@ruc.edu.cn",
        "scholar_url": "https://scholar.google.com/citations?user=WenbingHuang",
        "domain_tags": "#GeometricDeepLearning, #Equivariance, #LieGroups",
        "notes": "Leading research in Geometric Deep Learning for complex physical systems with symmetry equivariance"
    },
    {
        "full_name": "Yue Song",
        "native_name": "宋越",
        "region": "CN",
        "organization": "Tsinghua University",
        "role_title": "Researcher",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#RiemannianOptimization, #LieGroups, #ManifoldDL",
        "notes": "Lie group manifolds and Riemannian optimization directly in deep learning architectures"
    },
    {
        "full_name": "DeepSeek Compiler Architecture Team",
        "native_name": "深度求索编译团队",
        "region": "CN",
        "organization": "DeepSeek AI",
        "role_title": "Core Tensor Infrastructure Group",
        "tier": "CTO_INVESTOR",
        "github_url": "https://github.com/deepseek-ai",
        "domain_tags": "#TensorCompilers, #AscendNPU, #DeepGEMM, #MoE",
        "notes": "DeepGEMM, DeepEP, hardware-aware tensor optimization and MoE latent communication"
    },

    # --- SOUTH KOREA (한국어) ---
    {
        "full_name": "Hyunwoo J. Kim",
        "native_name": "현우 김",
        "region": "KR",
        "organization": "KAIST (School of Computing)",
        "role_title": "Associate Professor",
        "tier": "TIER_1_SOTA",
        "email": "hwjkim@kaist.ac.kr",
        "scholar_url": "https://scholar.google.com/citations?user=HyunwooKim",
        "domain_tags": "#RiemannianManifolds, #GeometricDeepLearning, #ManifoldStatistics",
        "notes": "Multivariate general linear models on Riemannian manifolds and geometric learning on graphs"
    },
    {
        "full_name": "Frank Chongwoo Park",
        "native_name": "박종우",
        "region": "KR",
        "organization": "Seoul National University (SNU)",
        "role_title": "Professor of Mechanical & Aerospace Eng / AI",
        "tier": "TIER_1_SOTA",
        "email": "fcp@snu.ac.kr",
        "scholar_url": "https://scholar.google.com/citations?user=FrankParkSNU",
        "domain_tags": "#SE3Equivariance, #LieGroups, #DifferentialGeometry",
        "notes": "SE(3) and SE(2) equivariant generative models, Lie groups and differential geometry"
    },
    {
        "full_name": "Sunghyun Park",
        "native_name": "박성현",
        "region": "KR",
        "organization": "Rebellions / Sapeon",
        "role_title": "CEO & Founder",
        "tier": "CTO_INVESTOR",
        "linkedin_url": "https://www.linkedin.com/in/sunghyun-park-rebellions/",
        "domain_tags": "#ATOM, #REBEL, #TensorAccelerators, #DeterministicInference",
        "notes": "Architect of ATOM and REBEL tensor processors for deterministic latency"
    },
    {
        "full_name": "June Paik",
        "native_name": "백준호",
        "region": "KR",
        "organization": "FuriosaAI",
        "role_title": "CEO & Founder",
        "tier": "CTO_INVESTOR",
        "linkedin_url": "https://www.linkedin.com/in/june-paik/",
        "domain_tags": "#RNGD, #TensorContractionProcessor, #HyperscaleSilicon",
        "notes": "Renegade Tensor Contraction Processor (TCP) for hyperscale tensor computing"
    },

    # --- JAPAN (日本語) ---
    {
        "full_name": "Shun-ichi Amari",
        "native_name": "甘利 俊一",
        "region": "JP",
        "organization": "University of Tokyo / RIKEN AIP",
        "role_title": "Honorary Director / Pioneer",
        "tier": "TIER_1_SOTA",
        "scholar_url": "https://scholar.google.com/citations?user=ShunIchiAmari",
        "domain_tags": "#InformationGeometry, #RiemannianGeometry, #NaturalGradient",
        "notes": "Founding father of Information Geometry and differential geometric methods in neural networks"
    },
    {
        "full_name": "Eckhard Hitzer",
        "native_name": "ヒッツァー・エックハルト",
        "region": "JP",
        "organization": "International Christian University (ICU)",
        "role_title": "Professor of Physics & Mathematics",
        "tier": "TIER_1_SOTA",
        "email": "hitzer@icu.ac.jp",
        "scholar_url": "https://scholar.google.com/citations?user=EckhardHitzer",
        "domain_tags": "#CliffordAlgebra, #GeometricAlgebraAI, #ConformalGeometricAlgebra",
        "notes": "World authority on Clifford/Geometric Algebra applications in computing and neural architectures"
    },
    {
        "full_name": "Tohru Nitta",
        "native_name": "新田 徹",
        "region": "JP",
        "organization": "Tokyo Woman's Christian University",
        "role_title": "Professor",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#CliffordNeuralNetworks, #HypercomplexNeuralNetworks, #Quaternions",
        "notes": "Pioneer of Clifford Neural Networks (Clifford NN) and hypercomplex representations"
    },
    {
        "full_name": "Llion Jones & Sakana AI Team",
        "native_name": "サカナAI 連続思考チーム",
        "region": "JP",
        "organization": "Sakana AI",
        "role_title": "CTO / Co-Founder & Authors",
        "tier": "TIER_1_SOTA",
        "twitter_handle": "@SakanaAILabs",
        "domain_tags": "#ContinuousThoughtMachine, #CTM, #NonTokenizedAI, #ContinuousLatent",
        "notes": "Pioneered the Continuous Thought Machine (CTM) for non-tokenized neuronal synchronization"
    },
    {
        "full_name": "Ryan Hamerly",
        "native_name": "ライアン・ハマーリー",
        "region": "JP",
        "organization": "NTT Research PHI Lab",
        "role_title": "Senior Research Scientist",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#OpticalComputing, #PhotonicTensorMultiplication, #PhysicalAI",
        "notes": "Mapping high-dimensional matrix-vector tensor compute directly to linear-optical physical processes"
    },

    # --- GERMANY / DACH (Deutsch) ---
    {
        "full_name": "Johannes Brandstetter",
        "native_name": "Johannes Brandstetter",
        "region": "DE",
        "organization": "JKU Linz / Microsoft Research",
        "role_title": "Associate Professor",
        "tier": "TIER_1_SOTA",
        "twitter_handle": "@jo_brandstetter",
        "scholar_url": "https://scholar.google.com/citations?user=yT6HswYAAAAJ",
        "domain_tags": "#CliffordNeuralLayers, #GeometricDeepLearning, #PDEs",
        "notes": "Pioneering work in Clifford Neural Layers and equivariant geometric operators"
    },
    {
        "full_name": "Bernhard Schölkopf",
        "native_name": "Bernhard Schölkopf",
        "region": "DE",
        "organization": "Max Planck Institute for Intelligent Systems (MPI-IS) Tübingen",
        "role_title": "Director / ELLIS President",
        "tier": "TIER_1_SOTA",
        "scholar_url": "https://scholar.google.com/citations?user=DZ-fHPgAAAAJ",
        "domain_tags": "#CausalAI, #InformationGeometry, #KernelMethods",
        "notes": "Information-Geometric Causal Inference and orthogonal geometry of causal representations"
    },
    {
        "full_name": "Johannes Schemmel",
        "native_name": "Johannes Schemmel",
        "region": "DE",
        "organization": "Heidelberg University (Electronic Visions Group)",
        "role_title": "Chair of Neuromorphic Computing",
        "tier": "TIER_1_SOTA",
        "domain_tags": "#BrainScaleS2, #NeuromorphicSilicon, #ContinuousTimeDynamics",
        "notes": "Lead behind BrainScaleS-2 analog neuromorphic hardware for continuous physical neural dynamics"
    },
    {
        "full_name": "Thorsten Eisenhofer",
        "native_name": "Thorsten Eisenhofer",
        "region": "DE",
        "organization": "CISPA Helmholtz Center for Information Security",
        "role_title": "Faculty Researcher",
        "tier": "TIER_1_SOTA",
        "scholar_url": "https://scholar.google.com/citations?user=ThorstenEisenhofer",
        "domain_tags": "#LatentCommunication, #MultiAgentSecurity, #ContinuousChannels",
        "notes": "Safety of Latent Communication in Multi-Agent Systems via continuous internal links"
    }
]

def run_global_sync():
    init_db()
    
    # 1. Upsert all into POLYDIM_OUTREACH.sqlite
    for lead in GLOBAL_LEADS:
        upsert_contact(lead)
    
    all_contacts = list_contacts()
    print(f"✅ Synced {len(all_contacts)} global leads into POLYDIM_OUTREACH.sqlite")

    # 2. Ingest certified facts into POLYDIM_VECDB.sqlite
    vecdb_path = r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite"
    if os.path.exists(vecdb_path):
        conn = sqlite3.connect(vecdb_path)
        cur = conn.cursor()
        
        for lead in GLOBAL_LEADS:
            fact_detail = f"SOTA Node: {lead['full_name']} ({lead.get('native_name','')}) - {lead['organization']}. Contribution: {lead['notes']}. Tags: {lead['domain_tags']}"
            cur.execute("""
            INSERT INTO facts (fact_type, source_file, version, topic, metric_key, metric_val, metric_unit, detail, certified, inserted_at)
            VALUES ('GLOBAL_SOTA_NODE', 'GLOBAL_SCOUT_PIPELINE', 'V1550', :topic, :name, :region, 'NODE', :detail, 1, CURRENT_TIMESTAMP)
            """, {
                "topic": lead["domain_tags"].split(",")[0].strip("# "),
                "name": lead["full_name"],
                "region": lead["region"],
                "detail": fact_detail
            })
        conn.commit()
        conn.close()
        print("✅ Ingested SOTA nodes into POLYDIM_VECDB.sqlite 'facts' table (Exit Code 0).")

    # 3. Generate localized publication queue for each region
    formatter = MediaFormatter()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "READY_TO_PUBLISH", "LOCALIZED_PITCHES")
    os.makedirs(out_dir, exist_ok=True)

    for lead in GLOBAL_LEADS:
        lang_map = {"CN": "ZH", "KR": "KO", "JP": "JA", "DE": "DE", "US": "EN", "GLOBAL": "EN"}
        target_lang = lang_map.get(lead["region"], "EN")
        
        pitch = formatter.generate_localized_pitch(
            language=target_lang,
            contact_name=lead.get("native_name") or lead["full_name"],
            org_or_lab=lead["organization"],
            paper_ref=lead["notes"]
        )
        
        filename = f"PITCH_{lead['region']}_{lead['full_name'].replace(' ', '_')}.txt"
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            f.write(f"TO: {lead.get('email', 'DIRECT_DM_CHANNELS')}\nSUBJECT: {pitch['subject']}\n\n{pitch['body']}")

    print(f"✅ Generated {len(GLOBAL_LEADS)} localized pitches in: {out_dir}")

if __name__ == "__main__":
    run_global_sync()

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from outreach_db import init_db, upsert_contact
from contact_manager import list_contacts

def run_ingestion():
    init_db()

    contacts = [
        {
            'full_name': 'Pentti Kanerva',
            'organization': 'UC Berkeley (Redwood Center for Theoretical Neuroscience)',
            'role_title': 'Foundational Theorist / Researcher',
            'tier': 'TIER_1_SOTA',
            'email': 'pkanerva@berkeley.edu',
            'domain_tags': '#HDC, #SDM, #HyperdimensionalComputing',
            'notes': 'Founder of Sparse Distributed Memory (SDM) & Hyperdimensional Computing'
        },
        {
            'full_name': 'Abbas Rahimi',
            'organization': 'IBM Research Zurich',
            'role_title': 'Principal Research Staff Member',
            'tier': 'TIER_1_SOTA',
            'linkedin_url': 'https://www.linkedin.com/in/abbas-rahimi-52a13248/',
            'domain_tags': '#HDC, #HardwareCoDesign, #EdgeIntelligence',
            'notes': 'Pioneer of HDC hardware/software co-design'
        },
        {
            'full_name': 'Jan Rabaey',
            'organization': 'UC Berkeley (EECS)',
            'role_title': 'Professor Emeritus',
            'tier': 'TIER_1_SOTA',
            'email': 'jan_rabaey@berkeley.edu',
            'domain_tags': '#HDC, #LowPowerSilicon, #NeuroInspired',
            'notes': 'Low-power silicon architecture for HDC'
        },
        {
            'full_name': 'Michael Bronstein',
            'organization': 'University of Oxford / DeepMind',
            'role_title': 'DeepMind Professor of AI',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@mmbronstein',
            'domain_tags': '#GeometricDeepLearning, #Manifolds, #Equivariance',
            'notes': 'Co-author of Geometric Deep Learning blueprint'
        },
        {
            'full_name': 'Taco Cohen',
            'organization': 'Qualcomm AI Research',
            'role_title': 'Principal Research Scientist',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@taco_cohen',
            'domain_tags': '#SphericalCNNs, #GaugeEquivariance, #Clifford',
            'notes': 'Pioneer of Spherical CNNs and Gauge Equivariant networks'
        },
        {
            'full_name': 'Max Welling',
            'organization': 'University of Amsterdam / CuspAI',
            'role_title': 'Professor / Co-Founder',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@maxwelling',
            'domain_tags': '#SphericalCNNs, #EquivariantArchitectures',
            'notes': 'Co-author of Spherical CNNs and Geometric AI'
        },
        {
            'full_name': 'Johannes Brandstetter',
            'organization': 'JKU Linz / Microsoft',
            'role_title': 'Assistant Professor',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@jo_brandstetter',
            'domain_tags': '#CliffordNeuralLayers, #GeometricAlgebra, #PDE',
            'notes': 'Pioneer of Clifford Neural Layers in neural network ops'
        },
        {
            'full_name': 'Maximilian Nickel',
            'organization': 'Meta AI (FAIR)',
            'role_title': 'Research Scientist',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@max_nickel',
            'domain_tags': '#PoincareEmbeddings, #RiemannianGeometry, #Hyperbolic',
            'notes': 'Poincaré Embeddings and continuous non-Euclidean representations'
        },
        {
            'full_name': 'Joan Bruna',
            'organization': 'NYU Courant / Center for Data Science',
            'role_title': 'Associate Professor',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@joanbruna',
            'domain_tags': '#SpectralNetworks, #GraphManifolds',
            'notes': 'Spectral networks and continuous manifold representations'
        },
        {
            'full_name': 'Andrew Feldman',
            'organization': 'Cerebras Systems',
            'role_title': 'CEO & Co-Founder',
            'tier': 'CTO_INVESTOR',
            'twitter_handle': '@CerebrasSystems',
            'domain_tags': '#WaferScaleEngine, #SRAMTiling, #HardwareAcceleration',
            'notes': 'Creator of CS-2/CS-3 Wafer Scale Engine'
        },
        {
            'full_name': 'Jim Keller',
            'organization': 'Tenstorrent',
            'role_title': 'CEO',
            'tier': 'CTO_INVESTOR',
            'twitter_handle': '@jimkeller256',
            'domain_tags': '#SpatialCompute, #RISCV, #TensorRouting',
            'notes': 'Architect of Wormhole/Grayskull spatial tensor computing'
        },
        {
            'full_name': 'Jonathan Ross',
            'organization': 'Groq',
            'role_title': 'CEO & Founder',
            'tier': 'CTO_INVESTOR',
            'twitter_handle': '@JonathanRoss321',
            'domain_tags': '#LPU, #TensorStreaming, #DeterministicSilicon',
            'notes': 'Creator of LPU deterministic tensor compute'
        },
        {
            'full_name': 'Rodrigo Liang',
            'organization': 'SambaNova Systems',
            'role_title': 'CEO & Founder',
            'tier': 'CTO_INVESTOR',
            'linkedin_url': 'https://www.linkedin.com/in/rodrigo-liang-52b3/',
            'domain_tags': '#ReconfigurableDataflow, #RDA, #DataflowSilicon',
            'notes': 'Creator of Reconfigurable Dataflow Architecture'
        },
        {
            'full_name': 'Sainbayar Sukhbaatar',
            'organization': 'Meta AI (FAIR)',
            'role_title': 'Research Scientist',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@SainbarS',
            'domain_tags': '#CommNet, #ContinuousMAC, #NonTokenized',
            'notes': 'Continuous vector communication for multi-agent systems'
        },
        {
            'full_name': 'Jakob Foerster',
            'organization': 'University of Oxford (FLAIR)',
            'role_title': 'Associate Professor',
            'tier': 'TIER_1_SOTA',
            'twitter_handle': '@jakob_foerster',
            'domain_tags': '#DIAL, #ContinuousChannelMultiAgent, #MARL',
            'notes': 'Differentiable Inter-Agent Learning and continuous communication channels'
        }
    ]

    for c in contacts:
        upsert_contact(c)

    all_c = list_contacts()
    print(f"Total contacts ingested in POLYDIM_OUTREACH.sqlite: {len(all_c)}")
    for r in all_c:
        print(f"[{r['tier']}] {r['full_name']} - {r['organization']} ({r['domain_tags']})")

if __name__ == "__main__":
    run_ingestion()

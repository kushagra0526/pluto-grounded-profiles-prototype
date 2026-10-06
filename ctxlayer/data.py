"""Synthetic voice-interview transcripts + an LLM-style claim extraction (fixture) for 6 made-up professionals.

The claim fixture stands in for what an extraction model would return from each call. Four of its claims
are deliberately wrong (inflated number, unmentioned skill, upgraded title, invented quote) so the
verifier has something real to catch. Visibility is what each person chose after reviewing their profile.
"""

TRANSCRIPTS = {
    "p1": [("00:20", "I'm a backend engineer, I've been doing this about six years now."),
           ("01:05", "Right now I'm a senior engineer at Northwind Pay, on the payments ledger team."),
           ("02:10", "I led a team of four that rebuilt our reconciliation pipeline in Go and Postgres."),
           ("03:30", "We cut settlement errors by about 40 percent after the rebuild."),
           ("05:00", "I want a remote role, ideally at an early-stage fintech."),
           ("06:15", "Honestly I'm looking quietly, my manager doesn't know."),
           ("07:40", "Compensation wise I'd want around 180k base."),
           ("08:30", "I'm in Austin and I'd stay here.")],
    "p2": [("00:15", "I do ML infrastructure, mostly training pipelines and evaluation."),
           ("01:20", "I'm a senior engineer at Lumen Labs right now."),
           ("02:40", "I built our evaluation harness in Python and PyTorch, it runs about 3,000 evals a night."),
           ("04:00", "We use Docker for everything, everything ships as containers."),
           ("05:30", "Next I want to work on agent evals at a research-heavy startup."),
           ("06:45", "I'd need visa sponsorship, I'm on an H-1B."),
           ("08:10", "I'm in San Francisco, happy to be in office.")],
    "p3": [("00:10", "I'm a product designer, about eight years in, mostly B2B SaaS."),
           ("01:30", "I was design lead at a logistics startup, we had three designers."),
           ("03:00", "I redesigned the onboarding and activation went from 22 to 31 percent."),
           ("04:20", "I work in Figma and I prototype in React when I need to."),
           ("06:00", "I want a founding designer role, remote or New York."),
           ("07:15", "I'm based in Brooklyn.")],
    "p4": [("00:25", "I'm a full stack engineer, four years, TypeScript and React mostly."),
           ("01:40", "I'm at Harbor Health building patient scheduling."),
           ("03:10", "I own our Node and GraphQL API, we serve about 200 clinics."),
           ("04:30", "I'd love a remote full stack role at a healthcare or climate company."),
           ("05:50", "I'm currently in Denver."),
           ("07:00", "Looking for around 150k.")],
    "p5": [("00:30", "I'm a data engineer, about five years, Spark, Airflow and dbt."),
           ("01:50", "I work at a retail analytics company, I'd rather not say which."),
           ("03:00", "I migrated our warehouse from Redshift to Snowflake and cut costs by 35 percent."),
           ("04:40", "I want to move into ML platform work, remote is a must."),
           ("06:10", "I'm in Toronto, so I'd need a company that hires in Canada.")],
    "p6": [("00:20", "I'm an engineering manager, I manage eight engineers on a platform team."),
           ("01:35", "I'm at Cobalt Cloud, before that I was an IC for six years."),
           ("03:00", "We moved our services to Kubernetes and I ran the on-call program."),
           ("04:30", "I want a head of engineering role at a seed or Series A company."),
           ("06:00", "I'm in Seattle and open to relocating to San Francisco."),
           ("07:20", "I'd want around 230k plus meaningful equity.")],
}

NAMES = {"p1": "Ana R.", "p2": "Dev K.", "p3": "Mira S.", "p4": "Jon P.", "p5": "Lee C.", "p6": "Sam O."}

# field, value, quote, timestamp
CLAIMS = {
    "p1": [("role", "backend engineer", "I'm a backend engineer", "00:20"),
           ("years", "6", "I've been doing this about six years now", "00:20"),
           ("title", "Senior Engineer", "I'm a senior engineer at Northwind Pay", "01:05"),
           ("employer", "Northwind Pay", "I'm a senior engineer at Northwind Pay", "01:05"),
           ("skills", "Go", "rebuilt our reconciliation pipeline in Go and Postgres", "02:10"),
           ("skills", "Postgres", "rebuilt our reconciliation pipeline in Go and Postgres", "02:10"),
           ("achievement", "Led a team of 12 that rebuilt the reconciliation pipeline", "I led a team of four that rebuilt our reconciliation pipeline", "02:10"),   # WRONG: 4, not 12
           ("achievement", "Cut settlement errors by about 40%", "We cut settlement errors by about 40 percent", "03:30"),
           ("wants", "remote role at an early-stage fintech", "I want a remote role, ideally at an early-stage fintech", "05:00"),
           ("search_status", "looking quietly", "I'm looking quietly, my manager doesn't know", "06:15"),
           ("salary", "180k base", "I'd want around 180k base", "07:40"),
           ("location", "Austin", "I'm in Austin and I'd stay here", "08:30")],
    "p2": [("role", "ML infrastructure engineer", "I do ML infrastructure, mostly training pipelines and evaluation", "00:15"),
           ("title", "Staff Engineer", "I'm a senior engineer at Lumen Labs right now", "01:20"),                    # WRONG: senior, not staff
           ("employer", "Lumen Labs", "I'm a senior engineer at Lumen Labs right now", "01:20"),
           ("skills", "Python", "I built our evaluation harness in Python and PyTorch", "02:40"),
           ("skills", "PyTorch", "I built our evaluation harness in Python and PyTorch", "02:40"),
           ("skills", "Kubernetes", "We use Docker for everything, everything ships as containers", "04:00"),       # WRONG: never said Kubernetes
           ("achievement", "Built an eval harness running about 3,000 evals a night", "it runs about 3,000 evals a night", "02:40"),
           ("wants", "agent evals at a research-heavy startup", "I want to work on agent evals at a research-heavy startup", "05:30"),
           ("visa", "needs sponsorship (H-1B)", "I'd need visa sponsorship, I'm on an H-1B", "06:45"),
           ("location", "San Francisco", "I'm in San Francisco, happy to be in office", "08:10")],
    "p3": [("role", "product designer", "I'm a product designer, about eight years in", "00:10"),
           ("years", "8", "about eight years in", "00:10"),
           ("title", "Design Lead", "I was design lead at a logistics startup", "01:30"),
           ("achievement", "Raised activation from 22% to 31% with an onboarding redesign", "activation went from 22 to 31 percent", "03:00"),
           ("skills", "Figma", "I work in Figma and I prototype in React", "04:20"),
           ("skills", "React", "I work in Figma and I prototype in React", "04:20"),
           ("wants", "founding designer role, remote or New York", "I want a founding designer role, remote or New York", "06:00"),
           ("location", "Brooklyn", "I'm based in Brooklyn", "07:15")],
    "p4": [("role", "full stack engineer", "I'm a full stack engineer, four years", "00:25"),
           ("years", "4", "four years", "00:25"),
           ("employer", "Harbor Health", "I'm at Harbor Health building patient scheduling", "01:40"),
           ("skills", "TypeScript", "TypeScript and React mostly", "00:25"),
           ("skills", "GraphQL", "I own our Node and GraphQL API", "03:10"),
           ("achievement", "Owns the API serving about 200 clinics", "we serve about 200 clinics", "03:10"),
           ("wants", "remote full stack role in healthcare or climate", "I'd love a remote full stack role at a healthcare or climate company", "04:30"),
           ("location", "Denver", "I'm currently in Denver", "05:50"),
           ("salary", "150k", "Looking for around 150k", "07:00")],
    "p5": [("role", "data engineer", "I'm a data engineer, about five years", "00:30"),
           ("skills", "Spark", "Spark, Airflow and dbt", "00:30"),
           ("skills", "Snowflake", "migrated our warehouse from Redshift to Snowflake", "03:00"),
           ("employer", "Shopline Analytics", "I work at Shopline Analytics on the warehouse team", "01:50"),          # WRONG: invented quote; they declined to name it
           ("achievement", "Cut warehouse costs by 35% moving Redshift to Snowflake", "cut costs by 35 percent", "03:00"),
           ("wants", "ML platform work, remote", "I want to move into ML platform work, remote is a must", "04:40"),
           ("location", "Toronto", "I'm in Toronto", "06:10")],
    "p6": [("role", "engineering manager", "I'm an engineering manager", "00:20"),
           ("achievement", "Manages 8 engineers on a platform team", "I manage eight engineers on a platform team", "00:20"),
           ("employer", "Cobalt Cloud", "I'm at Cobalt Cloud", "01:35"),
           ("skills", "Kubernetes", "We moved our services to Kubernetes", "03:00"),
           ("wants", "head of engineering at seed / Series A", "I want a head of engineering role at a seed or Series A company", "04:30"),
           ("location", "Seattle (open to SF)", "I'm in Seattle and open to relocating to San Francisco", "06:00"),
           ("salary", "230k plus equity", "I'd want around 230k plus meaningful equity", "07:20")],
}
PLANTED_WRONG = {("p1", "achievement", "Led a team of 12 that rebuilt the reconciliation pipeline"),
                 ("p2", "title", "Staff Engineer"), ("p2", "skills", "Kubernetes"), ("p5", "employer", "Shopline Analytics")}

# What each person chose to share after reviewing (private < companies < agents). Unlisted fields default to "private".
VISIBILITY_DEFAULT = {"role": "agents", "years": "agents", "title": "agents", "skills": "agents", "achievement": "agents",
                      "wants": "agents", "location": "agents", "employer": "private", "salary": "private",
                      "search_status": "private", "visa": "companies"}
VISIBILITY_OVERRIDES = {"p4": {"employer": "companies"}, "p6": {"employer": "agents", "salary": "companies"}}

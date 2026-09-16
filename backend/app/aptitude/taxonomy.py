"""
Normalized Aptitude Taxonomy for PlacementPilot AI Phase 2.
Defines 14 Domains and ~220 Subtopics with stable, unique slugs and exact display names.
"""

from typing import Dict, List, TypedDict


class SubtopicDef(TypedDict):
    name: str
    slug: str


class TopicDef(TypedDict):
    name: str
    slug: str
    subtopics: List[SubtopicDef]


class DomainDef(TypedDict):
    name: str
    slug: str
    topics: List[TopicDef]


TAXONOMY_DATA: List[DomainDef] = [
    {
        "name": "Number Systems",
        "slug": "number-systems",
        "topics": [
            {
                "name": "Core Number Concepts",
                "slug": "core-number-concepts",
                "subtopics": [
                    {"name": "Divisibility Rules", "slug": "divisibility-rules"},
                    {"name": "HCF", "slug": "hcf"},
                    {"name": "LCM", "slug": "lcm"},
                    {"name": "Unit Digit", "slug": "unit-digit"},
                    {"name": "Cyclicity", "slug": "cyclicity"},
                    {"name": "Remainder Theorem", "slug": "remainder-theorem"},
                    {"name": "Modular Arithmetic", "slug": "modular-arithmetic"},
                    {"name": "Wilson's Theorem", "slug": "wilsons-theorem"},
                    {"name": "Prime Numbers", "slug": "prime-numbers"},
                    {"name": "Composite Numbers", "slug": "composite-numbers"},
                    {"name": "Co-prime Numbers", "slug": "co-prime-numbers"},
                    {"name": "Rational Numbers", "slug": "rational-numbers"},
                    {"name": "Irrational Numbers", "slug": "irrational-numbers"},
                    {"name": "Natural Numbers", "slug": "natural-numbers"},
                    {"name": "Whole Numbers", "slug": "whole-numbers"},
                    {"name": "Integers", "slug": "integers"},
                    {"name": "Algebraic Identities", "slug": "algebraic-identities"},
                    {
                        "name": "Polynomial Remainder Theorem",
                        "slug": "polynomial-remainder-theorem",
                    },
                    {"name": "Factorial Remainders", "slug": "factorial-remainders"},
                    {
                        "name": "Two-Digit Number Reversal",
                        "slug": "two-digit-number-reversal",
                    },
                    {"name": "Consecutive Numbers", "slug": "consecutive-numbers"},
                    {"name": "Reciprocal Problems", "slug": "reciprocal-problems"},
                ],
            }
        ],
    },
    {
        "name": "Relations and Functions",
        "slug": "relations-and-functions",
        "topics": [
            {
                "name": "Relations and Sets",
                "slug": "relations-and-sets",
                "subtopics": [
                    {"name": "Relations", "slug": "relations"},
                    {"name": "Domain", "slug": "domain"},
                    {"name": "Co-domain", "slug": "co-domain"},
                    {"name": "Range", "slug": "range"},
                    {"name": "Reflexive Relation", "slug": "reflexive-relation"},
                    {"name": "Symmetric Relation", "slug": "symmetric-relation"},
                    {"name": "Transitive Relation", "slug": "transitive-relation"},
                    {"name": "One-One Function", "slug": "one-one-function"},
                    {"name": "Onto Function", "slug": "onto-function"},
                    {"name": "Bijective Function", "slug": "bijective-function"},
                    {"name": "Vertical Line Test", "slug": "vertical-line-test"},
                ],
            }
        ],
    },
    {
        "name": "Ratio and Proportion",
        "slug": "ratio-and-proportion",
        "topics": [
            {
                "name": "Ratios, Proportions and Applications",
                "slug": "ratios-proportions-and-applications",
                "subtopics": [
                    {"name": "Ratio", "slug": "ratio"},
                    {"name": "Proportion", "slug": "proportion"},
                    {"name": "Compound Ratio", "slug": "compound-ratio"},
                    {"name": "Duplicate Ratio", "slug": "duplicate-ratio"},
                    {"name": "Triplicate Ratio", "slug": "triplicate-ratio"},
                    {"name": "Sub-duplicate Ratio", "slug": "sub-duplicate-ratio"},
                    {"name": "Inverse Ratio", "slug": "inverse-ratio"},
                    {"name": "Mean Proportional", "slug": "mean-proportional"},
                    {"name": "Third Proportional", "slug": "third-proportional"},
                    {"name": "Fourth Proportional", "slug": "fourth-proportional"},
                    {"name": "Componendo", "slug": "componendo"},
                    {"name": "Dividendo", "slug": "dividendo"},
                    {"name": "Componendo and Dividendo", "slug": "componendo-and-dividendo"},
                    {"name": "Direct Proportion", "slug": "direct-proportion"},
                    {"name": "Inverse Proportion", "slug": "inverse-proportion"},
                    {"name": "Continued Proportion", "slug": "continued-proportion"},
                    {"name": "Comparison of Ratios", "slug": "comparison-of-ratios"},
                    {"name": "Division into Ratios", "slug": "division-into-ratios"},
                    {"name": "Ages Ratio", "slug": "ages-ratio"},
                    {
                        "name": "Income-Expenditure-Savings Ratio",
                        "slug": "income-expenditure-savings-ratio",
                    },
                    {"name": "Partnership Ratio", "slug": "partnership-ratio"},
                    {"name": "Coin Ratio", "slug": "coin-ratio"},
                    {"name": "Mixture Ratio", "slug": "mixture-ratio"},
                ],
            }
        ],
    },
    {
        "name": "Time and Work",
        "slug": "time-and-work",
        "topics": [
            {
                "name": "Work, Pipes and Efficiency",
                "slug": "work-pipes-and-efficiency",
                "subtopics": [
                    {"name": "Time and Work", "slug": "time-and-work"},
                    {"name": "One-Day Work Method", "slug": "one-day-work-method"},
                    {"name": "LCM Method", "slug": "lcm-method"},
                    {"name": "Efficiency Ratio", "slug": "efficiency-ratio"},
                    {
                        "name": "Inverse Efficiency-Time Relation",
                        "slug": "inverse-efficiency-time-relation",
                    },
                    {"name": "Alternating Work", "slug": "alternating-work"},
                    {"name": "Pipes and Cisterns", "slug": "pipes-and-cisterns"},
                    {"name": "Inlet and Outlet", "slug": "inlet-and-outlet"},
                    {"name": "Work and Wages", "slug": "work-and-wages"},
                    {
                        "name": "Men-Women-Children Work Equivalence",
                        "slug": "men-women-children-work-equivalence",
                    },
                    {"name": "Men Dropping Out", "slug": "men-dropping-out"},
                    {
                        "name": "Partner Joining and Leaving Work",
                        "slug": "partner-joining-and-leaving-work",
                    },
                    {"name": "Fractional Work", "slug": "fractional-work"},
                    {"name": "Total Work Method", "slug": "total-work-method"},
                ],
            }
        ],
    },
    {
        "name": "Profit and Loss",
        "slug": "profit-and-loss",
        "topics": [
            {
                "name": "Commercial Arithmetic",
                "slug": "commercial-arithmetic",
                "subtopics": [
                    {"name": "Cost Price", "slug": "cost-price"},
                    {"name": "Selling Price", "slug": "selling-price"},
                    {"name": "Profit", "slug": "profit"},
                    {"name": "Loss", "slug": "loss"},
                    {"name": "Profit Percentage", "slug": "profit-percentage"},
                    {"name": "Loss Percentage", "slug": "loss-percentage"},
                    {"name": "Marked Price", "slug": "marked-price"},
                    {"name": "Discount", "slug": "discount"},
                    {"name": "Discount Percentage", "slug": "discount-percentage"},
                    {"name": "Successive Discounts", "slug": "successive-discounts"},
                    {"name": "Dishonest Dealer", "slug": "dishonest-dealer"},
                    {"name": "False Weight", "slug": "false-weight"},
                    {"name": "Same Selling Price Trap", "slug": "same-selling-price-trap"},
                    {"name": "CP of m = SP of n", "slug": "cp-of-m-sp-of-n"},
                    {"name": "Profit on Selling Price", "slug": "profit-on-selling-price"},
                    {"name": "Loss on Selling Price", "slug": "loss-on-selling-price"},
                    {"name": "Overheads", "slug": "overheads"},
                    {"name": "Markup", "slug": "markup"},
                    {"name": "Buy x Get y Free", "slug": "buy-x-get-y-free"},
                    {"name": "Two Articles Same SP", "slug": "two-articles-same-sp"},
                    {
                        "name": "Mixture with Profit and Loss",
                        "slug": "mixture-with-profit-and-loss",
                    },
                ],
            }
        ],
    },
    {
        "name": "Percentages",
        "slug": "percentages",
        "topics": [
            {
                "name": "Percentage Applications",
                "slug": "percentage-applications",
                "subtopics": [
                    {"name": "Percentage", "slug": "percentage"},
                    {"name": "Percentage Increase", "slug": "percentage-increase"},
                    {"name": "Percentage Decrease", "slug": "percentage-decrease"},
                    {
                        "name": "Successive Percentage Change",
                        "slug": "successive-percentage-change",
                    },
                    {"name": "Population Growth", "slug": "percentage-population-growth"},
                    {"name": "Depreciation", "slug": "percentage-depreciation"},
                    {
                        "name": "Price-Consumption Relation",
                        "slug": "price-consumption-relation",
                    },
                    {"name": "Election and Votes", "slug": "election-and-votes"},
                    {"name": "Pass/Fail Set Theory", "slug": "pass-fail-set-theory"},
                    {"name": "Venn Diagram", "slug": "venn-diagram"},
                    {
                        "name": "Income-Expenditure-Savings",
                        "slug": "income-expenditure-savings",
                    },
                    {"name": "Percentage Miscellaneous", "slug": "percentage-miscellaneous"},
                    {"name": "Comparison of Percentages", "slug": "comparison-of-percentages"},
                ],
            }
        ],
    },
    {
        "name": "Simple Interest",
        "slug": "simple-interest",
        "topics": [
            {
                "name": "Simple Interest Concepts",
                "slug": "simple-interest-concepts",
                "subtopics": [
                    {"name": "Amount", "slug": "amount"},
                    {"name": "Principal", "slug": "principal"},
                    {"name": "Rate", "slug": "rate"},
                    {"name": "Time", "slug": "time"},
                    {"name": "Doubles and Triples", "slug": "doubles-and-triples"},
                    {"name": "Difference of Amounts", "slug": "difference-of-amounts"},
                    {"name": "SI Formula", "slug": "si-formula"},
                    {"name": "SI Relation with Principal", "slug": "si-relation-with-principal"},
                ],
            }
        ],
    },
    {
        "name": "Compound Interest",
        "slug": "compound-interest",
        "topics": [
            {
                "name": "Compound Interest Calculations",
                "slug": "compound-interest-calculations",
                "subtopics": [
                    {"name": "Annual Compounding", "slug": "annual-compounding"},
                    {"name": "Half-Yearly Compounding", "slug": "half-yearly-compounding"},
                    {"name": "Quarterly Compounding", "slug": "quarterly-compounding"},
                    {"name": "Compound Interest Formula", "slug": "compound-interest-formula"},
                    {"name": "Amount Formula", "slug": "amount-formula"},
                    {
                        "name": "CI and SI Difference for 2 Years",
                        "slug": "ci-and-si-difference-for-2-years",
                    },
                    {
                        "name": "CI and SI Difference for 3 Years",
                        "slug": "ci-and-si-difference-for-3-years",
                    },
                    {"name": "Finding Principal", "slug": "finding-principal"},
                    {"name": "Finding Rate", "slug": "finding-rate"},
                    {"name": "Finding Time", "slug": "finding-time"},
                    {
                        "name": "Fractional Time Compounding",
                        "slug": "fractional-time-compounding",
                    },
                    {"name": "Depreciation", "slug": "ci-depreciation"},
                    {"name": "Population Growth", "slug": "ci-population-growth"},
                    {"name": "CI and SI Relationship", "slug": "ci-and-si-relationship"},
                ],
            }
        ],
    },
    {
        "name": "Speed Time Distance",
        "slug": "speed-time-distance",
        "topics": [
            {
                "name": "Kinematics and Motion",
                "slug": "kinematics-and-motion",
                "subtopics": [
                    {"name": "Basic Speed Formula", "slug": "basic-speed-formula"},
                    {"name": "Average Speed", "slug": "speed-average-speed"},
                    {"name": "Relative Speed", "slug": "relative-speed"},
                    {
                        "name": "Same Direction Relative Speed",
                        "slug": "same-direction-relative-speed",
                    },
                    {
                        "name": "Opposite Direction Relative Speed",
                        "slug": "opposite-direction-relative-speed",
                    },
                    {"name": "Train Crossing Pole", "slug": "train-crossing-pole"},
                    {"name": "Train Crossing Platform", "slug": "train-crossing-platform"},
                    {"name": "Train Crossing Another Train", "slug": "train-crossing-another-train"},
                    {"name": "Boats and Streams", "slug": "boats-and-streams"},
                    {"name": "Downstream", "slug": "downstream"},
                    {"name": "Upstream", "slug": "upstream"},
                    {
                        "name": "Speed of Boat in Still Water",
                        "slug": "speed-of-boat-in-still-water",
                    },
                    {"name": "Speed of Stream", "slug": "speed-of-stream"},
                    {"name": "Races", "slug": "races"},
                    {"name": "Overtaking", "slug": "overtaking"},
                    {"name": "Meet and Return Formula", "slug": "meet-and-return-formula"},
                    {"name": "Walking and Resting", "slug": "walking-and-resting"},
                    {"name": "Planes at Right Angle", "slug": "planes-at-right-angle"},
                    {"name": "km/hr to m/s Conversion", "slug": "km-hr-to-m-s-conversion"},
                    {"name": "m/s to km/hr Conversion", "slug": "m-s-to-km-hr-conversion"},
                ],
            }
        ],
    },
    {
        "name": "Partnership",
        "slug": "partnership",
        "topics": [
            {
                "name": "Business Investments",
                "slug": "business-investments",
                "subtopics": [
                    {"name": "Simple Partnership", "slug": "simple-partnership"},
                    {"name": "Compound Partnership", "slug": "compound-partnership"},
                    {"name": "Capital × Time", "slug": "capital-times-time"},
                    {"name": "Profit Sharing Ratio", "slug": "profit-sharing-ratio"},
                    {"name": "Working Partner", "slug": "working-partner"},
                    {"name": "Sleeping Partner", "slug": "sleeping-partner"},
                    {"name": "Salary or Commission", "slug": "salary-or-commission"},
                    {"name": "Partner Joins Later", "slug": "partner-joins-later"},
                    {"name": "Partner Withdraws Capital", "slug": "partner-withdraws-capital"},
                    {
                        "name": "Investment Changes by Percentage",
                        "slug": "investment-changes-by-percentage",
                    },
                    {"name": "Finding Capital", "slug": "finding-capital"},
                    {"name": "Finding Profit", "slug": "finding-profit"},
                    {"name": "Difference in Shares", "slug": "difference-in-shares"},
                    {
                        "name": "Profit as Percentage of Capital",
                        "slug": "profit-as-percentage-of-capital",
                    },
                ],
            }
        ],
    },
    {
        "name": "Mixture and Alligation",
        "slug": "mixture-and-alligation",
        "topics": [
            {
                "name": "Alligation and Blends",
                "slug": "alligation-and-blends",
                "subtopics": [
                    {"name": "Alligation Rule", "slug": "alligation-rule"},
                    {"name": "Alligation Cross", "slug": "alligation-cross"},
                    {"name": "Mean Price", "slug": "mean-price"},
                    {"name": "Weighted Average", "slug": "alligation-weighted-average"},
                    {"name": "Equal Replacement", "slug": "equal-replacement"},
                    {"name": "Unequal Replacement", "slug": "unequal-replacement"},
                    {"name": "Repeated Replacement", "slug": "repeated-replacement"},
                    {
                        "name": "Removal and Replacement Formula",
                        "slug": "removal-and-replacement-formula",
                    },
                    {"name": "Mixing Two Mixtures", "slug": "mixing-two-mixtures"},
                    {"name": "Mixing Three Mixtures", "slug": "mixing-three-mixtures"},
                    {"name": "Three Ingredients", "slug": "three-ingredients"},
                    {
                        "name": "Profit and Loss Based Alligation",
                        "slug": "profit-and-loss-based-alligation",
                    },
                    {"name": "Interest Based Alligation", "slug": "interest-based-alligation"},
                    {
                        "name": "Time and Speed Based Alligation",
                        "slug": "time-and-speed-based-alligation",
                    },
                    {
                        "name": "Population Based Alligation",
                        "slug": "population-based-alligation",
                    },
                    {
                        "name": "Income-Expenditure Based Alligation",
                        "slug": "income-expenditure-based-alligation",
                    },
                    {"name": "Average Based Alligation", "slug": "average-based-alligation"},
                    {"name": "Milk and Water", "slug": "milk-and-water"},
                    {"name": "Acid and Water", "slug": "acid-and-water"},
                    {"name": "Sugar Solution", "slug": "sugar-solution"},
                    {"name": "Salt Solution", "slug": "salt-solution"},
                    {"name": "Alloys", "slug": "alloys"},
                    {"name": "Copper and Zinc", "slug": "copper-and-zinc"},
                    {"name": "Copper and Tin", "slug": "copper-and-tin"},
                    {"name": "Gold and Copper", "slug": "gold-and-copper"},
                    {"name": "Spirit and Water", "slug": "spirit-and-water"},
                    {"name": "Honey and Water", "slug": "honey-and-water"},
                    {"name": "Tea Mixture", "slug": "tea-mixture"},
                    {"name": "Coffee Mixture", "slug": "coffee-mixture"},
                    {"name": "Rice Mixture", "slug": "rice-mixture"},
                    {"name": "Pulses Mixture", "slug": "pulses-mixture"},
                    {"name": "Coin Mixture", "slug": "coin-mixture"},
                ],
            }
        ],
    },
    {
        "name": "Averages",
        "slug": "averages",
        "topics": [
            {
                "name": "Central Tendencies",
                "slug": "central-tendencies",
                "subtopics": [
                    {"name": "Simple Average", "slug": "simple-average"},
                    {"name": "Weighted Average", "slug": "averages-weighted-average"},
                    {"name": "Combined Average", "slug": "combined-average"},
                    {"name": "Average Marks", "slug": "average-marks"},
                    {"name": "Average Age", "slug": "average-age"},
                    {"name": "Average Weight", "slug": "average-weight"},
                    {"name": "Average Speed", "slug": "averages-average-speed"},
                    {"name": "Average Run per Wicket", "slug": "average-run-per-wicket"},
                ],
            }
        ],
    },
    {
        "name": "Mensuration",
        "slug": "mensuration",
        "topics": [
            {
                "name": "2D and 3D Geometry",
                "slug": "2d-and-3d-geometry",
                "subtopics": [
                    {"name": "Surface Area of Cube", "slug": "surface-area-of-cube"},
                    {"name": "Volume of Cube", "slug": "volume-of-cube"},
                    {"name": "Cubes Placed Adjacently", "slug": "cubes-placed-adjacently"},
                    {"name": "Volume of Cylinder", "slug": "volume-of-cylinder"},
                    {"name": "Area of Triangle", "slug": "area-of-triangle"},
                    {"name": "Ratio of Volumes", "slug": "ratio-of-volumes"},
                    {"name": "Ratio of Areas", "slug": "ratio-of-areas"},
                ],
            }
        ],
    },
    {
        "name": "Data Interpretation and Miscellaneous",
        "slug": "data-interpretation-and-miscellaneous",
        "topics": [
            {
                "name": "DI and Cross-Domain Applications",
                "slug": "di-and-cross-domain-applications",
                "subtopics": [
                    {"name": "Data Interpretation", "slug": "data-interpretation"},
                    {"name": "Approximation", "slug": "approximation"},
                    {"name": "Ratio and Ages", "slug": "ratio-and-ages"},
                    {"name": "Ratio and Wages", "slug": "ratio-and-wages"},
                    {"name": "Ratio and Coins", "slug": "ratio-and-coins"},
                    {"name": "Percentage and Population", "slug": "percentage-and-population"},
                    {"name": "Percentage and Income", "slug": "percentage-and-income"},
                    {
                        "name": "Percentage and Expenditure",
                        "slug": "percentage-and-expenditure",
                    },
                    {"name": "Percentage and Savings", "slug": "percentage-and-savings"},
                    {"name": "Percentage and Votes", "slug": "percentage-and-votes"},
                    {
                        "name": "Simple Interest and Alligation",
                        "slug": "simple-interest-and-alligation",
                    },
                    {
                        "name": "Compound Interest and Alligation",
                        "slug": "compound-interest-and-alligation",
                    },
                    {"name": "Speed and Alligation", "slug": "speed-and-alligation"},
                    {"name": "Profit and Alligation", "slug": "profit-and-alligation"},
                    {"name": "Average and Alligation", "slug": "average-and-alligation"},
                ],
            }
        ],
    },
]


def get_all_subtopic_slugs() -> List[str]:
    slugs = []
    for domain in TAXONOMY_DATA:
        for topic in domain["topics"]:
            for subtopic in topic["subtopics"]:
                slugs.append(subtopic["slug"])
    return slugs


def get_subtopic_map() -> Dict[str, Dict]:
    mapping = {}
    for domain in TAXONOMY_DATA:
        for topic in domain["topics"]:
            for subtopic in topic["subtopics"]:
                mapping[subtopic["slug"]] = {
                    "domain_name": domain["name"],
                    "domain_slug": domain["slug"],
                    "topic_name": topic["name"],
                    "topic_slug": topic["slug"],
                    "subtopic_name": subtopic["name"],
                    "subtopic_slug": subtopic["slug"],
                }
    return mapping

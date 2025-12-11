import json
import datetime
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('university_valuation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectValuator:
    def __init__(self, analysis_dir):
        self.analysis_dir = Path(analysis_dir)
        self.valuation_dir = self.analysis_dir / "valuations"
        self.market_analysis_dir = self.analysis_dir / "market_analysis"
        self.future_roadmap_dir = self.analysis_dir / "future_roadmap"
        self.reports_dir = self.analysis_dir / "reports"
        
        # Create directories if they don't exist
        for directory in [self.valuation_dir, self.market_analysis_dir, 
                         self.future_roadmap_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Load analysis data
        self.analysis = self._load_latest_analysis()
        
        # Initialize market data
        self.market_data = self._load_market_data()
        
        logger.info("ProjectValuator initialized successfully")
        
    def _load_latest_analysis(self):
        """Load the most recent analysis file"""
        analysis_files = list((self.analysis_dir / "analysis").glob("full_analysis_*.json"))
        if not analysis_files:
            logger.error("No analysis files found. Please run the analysis first.")
            return {}
            
        latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_market_data(self):
        """Load and cache market data from various sources"""
        return {
            'tech_sector_growth': {
                'ai_ml': 0.32,  # 32% annual growth
                'cloud_computing': 0.18,
                'cybersecurity': 0.25,
                'blockchain': 0.45,
                'iot': 0.28
            },
            'developer_salaries': {
                'us': {
                    'senior': 150000,
                    'mid': 110000,
                    'junior': 80000
                },
                'germany': {
                    'senior': 85000,
                    'mid': 65000,
                    'junior': 45000
                }
            },
            'funding_environment': {
                'seed_round': 2000000,
                'series_a': 10000000,
                'series_b': 30000000,
                'series_c': 75000000
            }
        }
        
        # Market rates (in USD) - Updated 2025 rates
        self.rates = {
            "development": {
                "backend": 120,  # $/hour
                "frontend": 110,
                "devops": 130,
                "data_science": 150,
                "ai_ml": 180,
                "mobile": 115,
                "blockchain": 200,
                "cloud_architect": 160
            },
            "design": {
                "ui_ux": 100,
                "graphic_design": 85,
                "ux_research": 120,
                "motion_design": 110
            },
            "management": {
                "project_management": 110,
                "product_management": 130,
                "scrum_master": 100,
                "technical_director": 180
            },
            "operations": {
                "devops_engineer": 140,
                "sre": 150,
                "cloud_engineer": 145
            },
            "data": {
                "data_engineer": 140,
                "data_scientist": 160,
                "ml_engineer": 175,
                "data_analyst": 120
            }
        }
        
        # Technology multipliers (based on current market demand)
        self.tech_multipliers = {
            'ai_ml': 1.8,
            'blockchain': 2.0,
            'cloud_native': 1.5,
            'iot': 1.4,
            'ar_vr': 1.7,
            'quantum': 2.5,
            'cybersecurity': 1.6
        }
        
    def calculate_development_costs(self):
        """Calculate the estimated development costs with detailed breakdown"""
        if not self.analysis:
            logger.error("No analysis data available")
            return {}
            
        total_hours = 0
        breakdown = defaultdict(float)
        tech_stack = defaultdict(int)
        
        # Calculate hours from code files with technology detection
        for file_path, analysis in self.analysis.get("code_analysis", {}).items():
            lines = analysis.get("line_count", 0)
            file_type = file_path.split('.')[-1].lower()
            
            # Estimate hours based on file type and size
            if file_type in ['py', 'js', 'java', 'c', 'cpp', 'go', 'rs', 'ts', 'jsx', 'tsx']:
                # Adjust hours based on file type complexity
                complexity = {
                    'py': 1.0, 'js': 1.1, 'java': 1.3, 'c': 1.5, 'cpp': 1.4,
                    'go': 1.2, 'rs': 1.6, 'ts': 1.1, 'jsx': 1.1, 'tsx': 1.2
                }.get(file_type, 1.0)
                
                hours = max(1, (lines / 100) * complexity)
                total_hours += hours
                breakdown[file_type] += hours
                
                # Detect technology stack
                if file_type in ['py']:
                    if any(imp in ' '.join(analysis.get('imports', [])) for imp in ['tensorflow', 'pytorch', 'sklearn']):
                        tech_stack['ai_ml'] += lines
                    elif any(imp in ' '.join(analysis.get('imports', [])) for imp in ['django', 'flask', 'fastapi']):
                        tech_stack['web_backend'] += lines
                elif file_type in ['js', 'ts', 'jsx', 'tsx']:
                    tech_stack['web_frontend'] += lines
                elif file_type in ['sol', 'rs']:
                    tech_stack['blockchain'] += lines
        
        # Calculate documentation hours with complexity factor
        doc_hours = len(self.analysis.get("documentation", {})) * 0.75  # 45 minutes per doc
        setup_hours = 60  # Initial setup and configuration (increased for modern devops)
        testing_hours = total_hours * 0.3  # 30% of dev time for testing
        devops_hours = total_hours * 0.2  # 20% for CI/CD and infrastructure
        
        total_hours += doc_hours + setup_hours + testing_hours + devops_hours
        
        # Calculate costs with role-based rates
        costs = {
            "development": total_hours * 0.5 * self.rates["development"]["backend"] +
                          total_hours * 0.3 * self.rates["development"]["frontend"] +
                          total_hours * 0.2 * self.rates["development"]["devops"],
            "documentation": doc_hours * self.rates["design"]["ui_ux"] * 0.8,
            "setup": setup_hours * self.rates["development"]["devops"],
            "testing": testing_hours * self.rates["development"]["backend"] * 0.8,
            "devops": devops_hours * self.rates["operations"]["devops_engineer"]
        }
        
        # Apply technology multipliers
        tech_multiplier = 1.0
        for tech, lines in tech_stack.items():
            if tech in self.tech_multipliers:
                tech_multiplier = max(tech_multiplier, self.tech_multipliers[tech])
        
        total_cost = sum(costs.values()) * tech_multiplier
        
        # Calculate time to market (in months)
        team_size = 5  # Average team size
        working_hours_per_month = 160  # 40 hours/week * 4 weeks
        time_to_market = (total_hours / (team_size * working_hours_per_month)) * 1.3  # 30% buffer
        
        return {
            "total_hours": round(total_hours, 2),
            "total_cost": round(total_cost, 2),
            "cost_breakdown": {k: round(v, 2) for k, v in costs.items()},
            "hourly_rate": round(total_cost / total_hours, 2) if total_hours > 0 else 0,
            "tech_stack": dict(tech_stack),
            "tech_multiplier": round(tech_multiplier, 2),
            "estimated_timeline_months": round(time_to_market, 1),
            "team_size_recommendation": team_size,
            "calculation_date": datetime.datetime.now().isoformat()
        }
    
    def generate_market_analysis(self):
        """Generate market analysis report"""
        # This would typically involve external API calls to get market data
        # For this example, we'll use placeholder data
        
        market_data = {
            "analysis_date": datetime.datetime.now().isoformat(),
            "comparable_companies": [
                {
                    "name": "Competitor A",
                    "valuation": 5000000,
                    "employees": 25,
                    "revenue": 2000000
                },
                {
                    "name": "Competitor B",
                    "valuation": 12000000,
                    "employees": 50,
                    "revenue": 5000000
                }
            ],
            "market_trends": {
                "ai_ml_adoption": "High growth (15% YoY)",
                "cloud_services": "Mature market (8% YoY)",
                "edge_computing": "Emerging (25% YoY)"
            },
            "valuation_multipliers": {
                "revenue": 5.2,  # Average revenue multiple
                "ebitda": 12.4,  # Average EBITDA multiple
                "users": 100     # $ per user for user-based valuation
            }
        }
        
        # Save market analysis
        with open(self.market_analysis_dir / "market_analysis.json", 'w') as f:
            json.dump(market_data, f, indent=2)
            
        return market_data
    
    def generate_future_roadmap(self):
        """Generate future development roadmap and potential value"""
        roadmap = {
            "timeline": {
                "short_term": [
                    "Optimize API performance",
                    "Enhance security features",
                    "Add user analytics"
                ],
                "mid_term": [
                    "Implement AI/ML capabilities",
                    "Expand to mobile platforms",
                    "Develop partner integrations"
                ],
                "long_term": [
                    "Blockchain integration",
                    "AR/VR features",
                    "Global expansion"
                ]
            },
            "potential_valuation_increase": {
                "short_term": "15-25%",
                "mid_term": "50-75%",
                "long_term": "150-300%"
            },
            "key_metrics": {
                "current_users": 1000,
                "projected_users_1y": 5000,
                "projected_users_3y": 25000,
                "current_mrr": 10000,
                "projected_mrr_1y": 75000,
                "projected_mrr_3y": 500000
            }
        }
        
        # Save roadmap
        with open(self.future_roadmap_dir / "future_roadmap.json", 'w') as f:
            json.dump(roadmap, f, indent=2)
            
        return roadmap
    
    def generate_valuation_report(self):
        """Generate comprehensive valuation report"""
        dev_costs = self.calculate_development_costs()
        market_data = self.generate_market_analysis()
        roadmap = self.generate_future_roadmap()
        
        # Calculate valuation using multiple methods
        cost_approach = dev_costs["total_cost"] * 1.5  # 1.5x cost
        market_approach = market_data["comparable_companies"][0]["valuation"] * 0.8  # 80% of closest competitor
        income_approach = roadmap["key_metrics"]["projected_mrr_3y"] * 12 * 3  # 3x ARR
        
        # Weighted average
        valuation = (cost_approach * 0.3 + 
                    market_approach * 0.4 + 
                    income_approach * 0.3)
        
        report = {
            "valuation_date": datetime.datetime.now().isoformat(),
            "current_valuation": {
                "cost_approach": cost_approach,
                "market_approach": market_approach,
                "income_approach": income_approach,
                "weighted_average": valuation
            },
            "development_costs": dev_costs,
            "market_analysis": market_data,
            "future_roadmap": roadmap,
            "sensitivity_analysis": {
                "best_case": valuation * 1.5,
                "base_case": valuation,
                "worst_case": valuation * 0.7
            },
            "recommendations": [
                "Focus on user acquisition to increase MRR",
                "Develop AI/ML features to increase valuation multiple",
                "Expand to new markets to diversify revenue streams"
            ]
        }
        
        # Save valuation report
        with open(self.valuation_dir / "valuation_report.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also save as Excel for easier reading
        self._save_as_excel(report)
        
        return report
    
    def _save_as_excel(self, report):
        # Create DataFrames for each section
        df_valuation = pd.DataFrame([{
            "Valuation Method": "Cost Approach",
            "Amount (USD)": report["current_valuation"]["cost_approach"],
            "Weight": "30%"
        }, {
            "Valuation Method": "Market Approach",
            "Amount (USD)": report["current_valuation"]["market_approach"],
            "Weight": "40%"
        }, {
            "Valuation Method": "Income Approach",
            "Amount (USD)": report["current_valuation"]["income_approach"],
            "Weight": "30%"
        }, {
            "Valuation Method": "Weighted Average",
            "Amount (USD)": report["current_valuation"]["weighted_average"],
            "Weight": "100%"
        }])
        
        df_costs = pd.DataFrame([{
            "Category": "Development",
            "Hours": report["development_costs"]["total_hours"],
            "Rate (USD/hour)": report["development_costs"]["hourly_rate"],
            "Total (USD)": report["development_costs"]["cost_breakdown"]["development"]
        }, {
            "Category": "Documentation",
            "Hours": report["development_costs"]["cost_breakdown"]["documentation"] / report["development_costs"]["hourly_rate"],
            "Rate (USD/hour)": report["development_costs"]["hourly_rate"] * 0.8,
            "Total (USD)": report["development_costs"]["cost_breakdown"]["documentation"]
        }, {
            "Category": "Setup",
            "Hours": report["development_costs"]["cost_breakdown"]["setup"] / report["development_costs"]["hourly_rate"],
            "Rate (USD/hour)": report["development_costs"]["hourly_rate"],
            "Total (USD)": report["development_costs"]["cost_breakdown"]["setup"]
        }])
        
        # Create Excel writer
        with pd.ExcelWriter(self.valuation_dir / "valuation_report.xlsx") as writer:
            df_valuation.to_excel(writer, sheet_name="Valuation", index=False)
            df_costs.to_excel(writer, sheet_name="Cost Breakdown", index=False)
            
            # Add market analysis
            df_market = pd.DataFrame(report["market_analysis"]["comparable_companies"])
            df_market.to_excel(writer, sheet_name="Market Analysis", index=False)
            
            # Add roadmap
            df_roadmap = pd.DataFrame([{
                "Timeline": "Short Term",
                "Initiatives": "\n".join(report["future_roadmap"]["timeline"]["short_term"])
            }, {
                "Timeline": "Mid Term",
                "Initiatives": "\n".join(report["future_roadmap"]["timeline"]["mid_term"])
            }, {
                "Timeline": "Long Term",
                "Initiatives": "\n".join(report["future_roadmap"]["timeline"]["long_term"])
            }])
            df_roadmap.to_excel(writer, sheet_name="Roadmap", index=False)

if __name__ == "__main__":
    valuator = ProjectValuator(r"D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital")
    report = valuator.generate_valuation_report()
    print(f"Valuation report generated at: {valuator.valuation_dir / 'valuation_report.xlsx'}")

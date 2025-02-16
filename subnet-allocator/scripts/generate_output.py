import json
from datetime import datetime

def generate_report():
    try:
        with open('allocation_results.json') as f:
            data = json.load(f)
        
        report = f"""CIDR Allocation Report
{'='*40}
Date: {datetime.now().isoformat()}
Request Type: {data.get('type', 'N/A')}
Original CIDR: {data.get('original_cidr', 'N/A')}
Status: {data['status'].upper()}

Allocated CIDRs:
{'-'*40}"""
        
        if data['status'] == 'success':
            for idx, cidr in enumerate(data['allocated_cidrs'], 1):
                report += f"\n{idx}. {cidr}"
                
            report += f"\n\nDatabase updated successfully in ccoe_subnets"
        else:
            report += f"\nERROR: {data.get('message', 'Unknown error')}"
            
        with open('cidr_allocation_report.txt', 'w') as f:
            f.write(report)
            
    except Exception as e:
        print(f"Report generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    generate_report()

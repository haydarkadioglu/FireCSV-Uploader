import csv
import random
from datetime import datetime, timedelta

def create_sample_csv():
    """Create sample employees CSV file in English"""
    
    # Sample data
    first_names = [
        "John", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Ashley", 
        "William", "Amanda", "James", "Jennifer", "Christopher", "Michelle", "Daniel", 
        "Lisa", "Matthew", "Angela", "Anthony", "Kimberly", "Mark", "Donna", "Donald", 
        "Carol", "Steven", "Ruth", "Paul", "Sharon", "Andrew", "Laura", "Joshua", 
        "Sandra", "Kenneth", "Cynthia", "Kevin", "Amy", "Brian", "Shirley", "George", 
        "Deborah", "Edward", "Rachel", "Ronald", "Carolyn", "Timothy", "Janet", 
        "Jason", "Catherine", "Jeffrey", "Frances"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", 
        "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", 
        "Mitchell", "Carter", "Roberts"
    ]
    
    departments = [
        "Information Technology", "Human Resources", "Finance", "Marketing", 
        "Sales", "Operations", "Customer Service", "Research and Development",
        "Quality Assurance", "Administration"
    ]
    
    positions = [
        "Software Engineer", "Project Manager", "Business Analyst", "HR Specialist",
        "Financial Analyst", "Marketing Coordinator", "Sales Representative", 
        "Operations Manager", "Customer Support Specialist", "Research Scientist",
        "QA Engineer", "Administrative Assistant", "Team Lead", "Senior Developer",
        "Product Manager", "Data Analyst", "Accountant", "Marketing Manager"
    ]
    
    cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
        "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
        "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville",
        "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento"
    ]
    
    states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]
    
    # Generate sample data
    employees = []
    
    for i in range(50):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate random hire date (last 5 years)
        start_date = datetime.now() - timedelta(days=5*365)
        random_days = random.randint(0, 5*365)
        hire_date = start_date + timedelta(days=random_days)
        
        employee = {
            "employee_id": f"EMP{str(i+1).zfill(4)}",
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@company.com",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "department": random.choice(departments),
            "position": random.choice(positions),
            "salary": random.randint(35000, 150000),
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "city": random.choice(cities),
            "state": random.choice(states),
            "zip_code": f"{random.randint(10000, 99999)}",
            "is_active": random.choice([True, True, True, False]),  # 75% active
            "manager_id": f"EMP{str(random.randint(1, min(i+1, 10))).zfill(4)}" if i > 0 else None,
            "performance_score": round(random.uniform(2.5, 5.0), 1),
            "years_experience": random.randint(1, 15),
            "education_level": random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
            "remote_work": random.choice([True, False])
        }
        
        employees.append(employee)
    
    # Write to CSV
    fieldnames = [
        "employee_id", "first_name", "last_name", "full_name", "email", "phone", 
        "department", "position", "salary", "hire_date", "city", "state", 
        "zip_code", "is_active", "manager_id", "performance_score", 
        "years_experience", "education_level", "remote_work"
    ]
    
    with open('sample_employees.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(employees)
    
    print("✅ Sample employees CSV file created successfully!")
    print("📄 File: sample_employees.csv")
    print(f"👥 Contains: {len(employees)} sample employee records")
    print("\n📋 Columns included:")
    for field in fieldnames:
        print(f"   • {field}")
    
    print("\n🔧 Use this file to test your Firebase CSV Uploader!")
    print("🚀 You can upload this to different collections/sub-collections for testing.")

if __name__ == "__main__":
    create_sample_csv()

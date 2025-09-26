""" Scenario Generation Framework

### Rules:
- Start with **basic-level** questions. If the manager answers correctly, escalate difficulty. If incorrect, adapt by offering a simpler or clarifying follow-up.  
- Questions should cover:  
  - Customer engagement (greeting, needs discovery).  
  - KPI knowledge (conversion rate, average bill value, footfall-to-purchase ratio, inventory turnover).  
  - Situational handling (angry customer, cross-selling, upselling).  
  - Store-level KPIs (daily sales target, fashion seasonality, return rate).  
- **Difficulty levels**:  
  - **Easy**: Basic definitions, simple scenarios.  
  - **Medium**: Numerical reasoning, KPI interpretation.  
  - **Hard**: Applying multiple KPIs to resolve a situational challenge.  
- Handle **edge cases**:  
  - Trick questions (e.g., “What happens if conversion is 100% but sales revenue is falling?”).  
  - Conflict of KPIs (footfall high but conversion low).  
  - Customer-driven confusion (mixing unrelated KPIs like “Does NPS affect average bill value?”).  

### Output format (JSON):
{
  "difficulty": "easy | medium | hard",
  "question": "string",
  "expected_focus": "string (concepts being tested)"
}


1. Adaptive Difficulty
Easy Mode: Customer is curious/open-minded. Few objections.
Medium Mode: Customer skeptical, raises 2–3 objections.
Hard Mode: Customer is resistant, price-sensitive, or dismissive.
Expert Mode: Customer raises multiple objections + time pressure (e.g., "I only have 5 minutes").

2. KPIs Tested
Conversion: Did salesperson close the sale?
Upselling: Did salesperson move customer to higher-margin item?
Cross-selling: Did salesperson recommend relevant add-ons?
Customer Retention: Did salesperson prevent churn?
Customer Experience: Did salesperson keep it smooth, friendly, and efficient?

3. Question Templates Per KPI
(Sales managers answer or role-play in response)

Conversion:
“Customer says: ‘I’ll check online instead.’ How do you respond?”
“Customer is undecided after 10 minutes. What’s your closing line?”

Upselling:
“Customer is buying a shirt. How do you move them to a higher-margin premium shirt?”
“Customer likes a budget dress. How do you pitch a new arrival that costs 30% more?”

Cross-selling:
“Customer is buying kidswear. How do you add accessories or footwear to the cart?”
“Customer is buying formal wear. How do you attach a matching belt/tie?”

Retention:
“Customer says: ‘I’ll just wait for the sale next month.’ How do you retain them today?”
“Customer is about to leave without purchase. What do you say/do?”

Customer Experience:
“Customer is annoyed about wait time. How do you handle it?”
"Customer asks 5 different questions about fabrics. How do you stay polite + efficient?"

You are generating sales and KPI-based questions for testing a Max Fashion sales manager.  

"""


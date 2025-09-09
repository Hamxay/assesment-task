# 🎯 AI Talent Recruiter - Multi-Agent System

An intelligent recruitment system powered by three specialized AI agents that evaluate candidates based on work experience, technical skills, and cultural fit.

## 🚀 Features

### 🤖 Multi-Agent Architecture
- **Experience Agent**: Evaluates work history, career progression, and industry relevance
- **Skills Agent**: Assesses technical competencies, certifications, and project experience  
- **Culture Agent**: Analyzes communication style, teamwork, and values alignment

### 💬 Human-in-the-Loop Interface
- Interactive conversational UI for detailed insights
- Real-time candidate evaluation and recommendations
- Customizable job descriptions and evaluation criteria
- Export capabilities for further analysis

### 📊 Advanced Analytics
- Score comparison charts and visualizations
- Performance summaries by agent type
- Candidate ranking and shortlisting
- Detailed recommendations and insights

## 🛠️ Installation

1. **Clone the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
LYZR_API_KEY=your_lyzr_api_key_here
```

**Note**: The system works without an API key using mock responses for demonstration purposes.

4. **Prepare your data**
- Place your candidates Excel file as `Candidates Sheet.xlsx`
- Optionally create a `job_description.txt` file with your job requirements

## 🚀 Usage

### Starting the Application
```bash
streamlit run app.py
```

### Workflow

1. **Setup Phase**
   - Upload or modify job description
   - Review candidate data
   - Configure evaluation parameters

2. **Evaluation Phase**
   - AI agents analyze candidates
   - Real-time progress tracking
   - Multi-dimensional scoring

3. **Results Phase**
   - View comprehensive analytics
   - Explore top candidates
   - Analyze agent performance

4. **Interactive Chat**
   - Ask questions about candidates
   - Get personalized recommendations
   - Deep dive into specific criteria

## 📁 Project Structure

```
ai-talent-recruiter/
├── app.py                 # Main Streamlit application
├── multi_agent_system.py  # Multi-agent coordinator
├── agents.py              # Individual AI agents
├── data_processor.py      # Data handling and preprocessing
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── Candidates Sheet.xlsx  # Candidate data (your file)
└── job_description.txt   # Job requirements
```

## 🤖 Agent Details

### Experience Agent
- **Focus**: Work history and career progression
- **Criteria**: Years of experience, job stability, industry relevance
- **Output**: Experience score, career progression analysis, recommendations

### Skills Agent  
- **Focus**: Technical competencies and certifications
- **Criteria**: Skill match, certifications, project experience
- **Output**: Skills score, technical assessment, skill gaps

### Culture Agent
- **Focus**: Cultural fit and soft skills
- **Criteria**: Communication style, teamwork, values alignment
- **Output**: Culture score, communication analysis, fit assessment

## 🔧 Configuration

### Agent Weights
Modify the scoring weights in `multi_agent_system.py`:
```python
weights = {"experience": 0.4, "skills": 0.4, "culture": 0.2}
```

### API Configuration
Update `config.py` for different AI providers:
```python
LYZR_API_KEY = os.getenv('LYZR_API_KEY')
LYZR_BASE_URL = "https://api.lyzr.ai"
```

## 📊 Data Format

### Expected Candidate Data Structure
The system expects an Excel file with LinkedIn profile data including:
- `firstName`, `lastName`
- `headline`, `about`, `location`
- `experience` (JSON array)
- `skills`, `topSkills` (JSON arrays)
- `education`, `certifications` (JSON arrays)
- `connectionsCount`, `followerCount`

### Job Description Format
Plain text file with:
- Job title and requirements
- Required skills and experience
- Responsibilities and expectations
- Company culture information


# 🛢️ IOCL PolicyBot
### Bilingual AI Chatbot for IT Policies & CDA Rules

A fully **offline**, bilingual (Hindi + English) chatbot for IOCL officers to query IT Policies and CDA (Conduct, Discipline & Appeal) Rules.

---

## 🏗️ Architecture

```
IOCL_ChatBot/
├── Backend/
│   └── IOCLChatBot/              ← .NET 8 Core C# Web API (MVC)
│       ├── Controllers/
│       │   ├── ChatController.cs       ← /api/chat endpoints
│       │   └── KnowledgeController.cs  ← /api/knowledge endpoints
│       ├── Models/
│       │   ├── ChatRequest.cs
│       │   ├── ChatResponse.cs
│       │   └── KnowledgeEntry.cs
│       ├── Services/
│       │   ├── IChatService.cs + ChatService.cs           ← Core logic
│       │   ├── IKnowledgeBaseService.cs + KnowledgeBaseService.cs ← Search
│       │   └── ILanguageService.cs + LanguageService.cs  ← Lang detect
│       ├── Data/
│       │   └── KnowledgeBase.json      ← All policies (bilingual)
│       ├── Program.cs
│       └── IOCLChatBot.csproj
├── Frontend/
│   ├── app.py                    ← Streamlit Python frontend
│   └── requirements.txt
├── .vscode/
│   ├── launch.json               ← VS Code run configs
│   ├── tasks.json
│   └── extensions.json
├── start.bat                     ← Windows quick start
├── start.sh                      ← Linux/Mac quick start
└── README.md
```

### MVC Pattern
| Layer | Technology | File |
|-------|-----------|------|
| **Model** | C# classes | `Models/*.cs`, `Data/KnowledgeBase.json` |
| **View** | Streamlit Python | `Frontend/app.py` |
| **Controller** | ASP.NET Core | `Controllers/*.cs` |
| **Service** | C# Services | `Services/*.cs` |

---

## ✅ Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| .NET SDK | 8.0+ | https://dotnet.microsoft.com/download |
| Python | 3.9+ | https://www.python.org/downloads/ |
| VS Code | Latest | https://code.visualstudio.com/ |

---

## 🚀 Quick Start

### Option A — One-click (Recommended)

**Windows:**
```
Double-click start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Option B — Manual (VS Code)

1. Open the project folder in VS Code:
   ```
   File → Open Folder → IOCL_ChatBot
   ```

2. Install recommended VS Code extensions when prompted (C# DevKit, Python)

3. **Terminal 1 — Start Backend:**
   ```bash
   cd Backend/IOCLChatBot
   dotnet run
   ```
   Backend runs at: `http://localhost:5000`

4. **Terminal 2 — Start Frontend:**
   ```bash
   pip install -r Frontend/requirements.txt
   cd Frontend
   streamlit run app.py
   ```
   Frontend opens at: `http://localhost:8501`

5. Or use VS Code Run & Debug (`F5`) → Select **"🚀 Run Full App"**

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Chatbot UI (Streamlit) | http://localhost:8501 |
| Backend API | http://localhost:5000 |
| Swagger API Docs | http://localhost:5000/swagger |
| Health Check | http://localhost:5000/api/chat/health |

---

## 📚 Knowledge Base Coverage

### IT Policies
| Policy ID | Topic |
|-----------|-------|
| IT-001 | Official Email Usage Policy |
| IT-002 | Internet & Social Media Policy |
| IT-003 | Password & Access Control Policy |
| IT-004 | Data Security & Classification |
| IT-005 | Device & IT Asset Management |
| IT-006 | Remote Work & VPN Policy |
| IT-007 | Cybersecurity Incident Response |

### CDA Rules
| Rule ID | Topic |
|---------|-------|
| CDA-001 | General Conduct Obligations |
| CDA-002 | Gifts, Hospitality & Conflict of Interest |
| CDA-003 | Disciplinary Proceedings & Penalties |
| CDA-004 | Outside Employment & Private Business |
| CDA-005 | Political Activities |

All entries are fully bilingual (English + हिंदी).

---

## 🔌 API Reference

### POST /api/chat
Send a message and get a policy-aware response.

**Request:**
```json
{
  "message": "What is the email policy?",
  "language": "en",
  "sessionId": "abc-123"
}
```

**Response:**
```json
{
  "answer": "**Official Email Usage Policy**\n\n...",
  "category": "IT Policy",
  "language": "en",
  "relatedTopics": ["Password Policy", "Data Security"],
  "policyReference": "IOCL-IT-POL-001",
  "found": true,
  "sessionId": "abc-123"
}
```

### GET /api/knowledge
Browse all policies: `GET /api/knowledge?lang=hi&category=IT Policy`

### GET /api/knowledge/search
Search: `GET /api/knowledge/search?q=password&lang=en`

### GET /api/chat/health
Health check for backend status monitoring.

---

## 💬 Sample Questions

**English:**
- "What is the email policy?"
- "Can I accept gifts from vendors?"
- "How often must I change my password?"
- "What is the process for disciplinary proceedings?"
- "What to do during a cyber attack?"
- "Can I do freelance work outside IOCL?"

**Hindi:**
- "ईमेल नीति क्या है?"
- "क्या मैं विक्रेता से उपहार ले सकता हूँ?"
- "पासवर्ड कितने दिनों में बदलना है?"
- "साइबर हमले में क्या करें?"
- "CDA नियमों के तहत क्या दंड हैं?"

---

## ➕ Adding New Policies

Edit `Backend/IOCLChatBot/Data/KnowledgeBase.json` and add a new entry:

```json
{
  "Id": "IT-008",
  "Category": "IT Policy",
  "SubCategory": "Your Sub Category",
  "PolicyReference": "IOCL-IT-POL-008",
  "Keywords": ["keyword1", "keyword2"],
  "KeywordsHi": ["हिंदी कीवर्ड"],
  "TitleEn": "English Title",
  "TitleHi": "हिंदी शीर्षक",
  "AnswerEn": "Full English answer...",
  "AnswerHi": "पूर्ण हिंदी उत्तर...",
  "RelatedIds": ["IT-001"]
}
```

No code changes needed — restart the backend and the new policy is live.

---

## 🔒 Offline Capability

This chatbot is **fully offline**:
- Knowledge base is a local JSON file
- Language detection uses Unicode ranges (no external API)
- No internet connection required at runtime
- All data stays within IOCL's network

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `dotnet: not found` | Install .NET 8 SDK from microsoft.com |
| `streamlit: not found` | Run `pip install streamlit` |
| Backend offline (red indicator) | Run `dotnet run` in `Backend/IOCLChatBot/` |
| Port 5000 in use | Change `"Urls": "http://localhost:5001"` in `appsettings.json` and update `BACKEND_URL` in `Frontend/app.py` |
| Hindi text not displaying | Ensure your system has Devanagari font support |

---

## 👨‍💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend language | C# (.NET 8) |
| Backend framework | ASP.NET Core Web API (MVC) |
| Frontend | Python + Streamlit |
| Architecture | MVC (Model-View-Controller) |
| Knowledge storage | JSON (offline) |
| Language detection | Unicode range analysis |
| Search | Keyword scoring algorithm |
| IDE | VS Code |

# 🚀 Vercel Deployment Guide - Cricket Strategy AI

## **Pre-Deployment Checklist**

- [x] `vercel.json` created
- [x] `package.json` at root created
- [x] `api/index.py` created (serverless entry point)
- [x] `requirements.txt` updated with FastAPI & uvicorn
- [x] `.env.example` created
- [x] `.gitignore` updated for Vercel

---

## **Deployment Steps**

### **1. Install Vercel CLI**
```bash
npm install -g vercel
```

### **2. Link Project to Vercel**
```bash
vercel link
```
Follow the prompts to:
- Create new project or select existing
- Choose directory: `./`
- Configure build settings (Vercel auto-detects)

### **3. Set Environment Variables**

On Vercel Dashboard:
```
Dashboard → Your Project → Settings → Environment Variables
```

Add:
```
GROQ_API_KEY=your_groq_api_key_here
NODE_ENV=production
VITE_API_URL=https://your-domain.vercel.app/api
```

### **4. Deploy**
```bash
# Development preview
vercel

# Production deployment
vercel --prod
```

---

## **Project Structure for Vercel**

```
cricket_statergy_ai/
├── vercel.json                    ← Vercel config
├── package.json                   ← Root npm config
├── requirements.txt               ← Python dependencies
├── .env.example                   ← Environment template
│
├── api/
│   ├── index.py                  ← ⭐ Serverless entry point
│   ├── main.py                   ← Original FastAPI app
│   └── llm_engine.py
│
├── frontend/                      ← React + Vite
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── dist/                      ← Build output
│
├── data/
│   └── batsman_features.csv       ← Pre-computed features
│
└── utils/
    ├── statergy_ingine.py
    └── strategy_engine.py
```

---

## **Key Configuration Files**

### **vercel.json**
- Routes API requests to `/api/index.py`
- Builds frontend with `npm run build --prefix frontend`
- Sets Python runtime to 3.11
- Configures environment variables

### **api/index.py**
- Entry point for all API requests
- Uses OS-agnostic paths (no Windows paths!)
- Handler for ASGI (FastAPI)
- Properly loads data files

### **Requirements**
- FastAPI 0.104.1
- Uvicorn for ASGI
- All ML dependencies (scikit-learn, pandas, numpy)
- Groq for LLM

---

## **Important Changes Made**

### **❌ Removed:**
- Windows-specific paths like `r"C:\Users\vishal\Desktop\..."`
- Direct `.env` usage at root

### **✅ Added:**
- OS-agnostic path handling using `os.path.join()`
- Proper ASGI handler for Vercel
- Environment variable support
- Error handling for missing data

### **✔️ Modified:**
- `requirements.txt` - added FastAPI, uvicorn, groq
- `.gitignore` - added Vercel-specific exclusions
- `package.json` at root for Vercel recognition

---

## **Troubleshooting**

### **"Module not found" error**
```python
# Make sure api/index.py has proper imports:
sys.path.insert(0, PROJECT_ROOT)
from statergy_ingine import generate_strategy
```

### **Data file not found**
Ensure `data/batsman_features.csv` exists in production:
- Upload to Vercel or generate during build
- Modify `get_data_path()` to use an API or cloud storage

### **Cold start timeout**
- Model loading takes time
- Consider caching models in memory
- Increase function timeout in `vercel.json`

### **CORS errors from frontend**
Vercel dashboard → Settings → Domains → add your domain

---

## **Frontend Deployment**

Frontend builds to `frontend/dist/`:
```bash
cd frontend
npm install
npm run build
```

Vercel automatically handles routing to:
- `/api/*` → Python API
- `/` → React app

---

## **Testing Locally Before Deploy**

```bash
# Test Python API locally
pip install -r requirements.txt
uvicorn api.index:app --reload

# Test frontend locally
cd frontend
npm run dev

# Or use Vercel CLI
vercel dev
```

---

## **Post-Deployment**

1. ✅ Visit: `https://your-domain.vercel.app`
2. ✅ Check API: `https://your-domain.vercel.app/api/health`
3. ✅ Check deployment logs: Dashboard → Deployments → View logs

---

## **Next Steps**

- [ ] Move data to cloud storage (AWS S3, Supabase) for production
- [ ] Implement database for caching strategy results
- [ ] Add authentication for sensitive endpoints
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Add CI/CD pipeline with GitHub Actions

---

**Ready to deploy! 🚀**

using IOCLChatBot.Models;

namespace IOCLChatBot.Services
{
    /// <summary>
    /// Core chat service: orchestrates knowledge lookup and response generation.
    /// Fully offline – no external AI API required.
    /// </summary>
    public class ChatService : IChatService
    {
        private readonly IKnowledgeBaseService _kb;
        private readonly ILanguageService _lang;
        private readonly ILogger<ChatService> _logger;

        // Session-based conversation history (in-memory for offline use)
        private static readonly Dictionary<string, List<string>> _sessionHistory = new();

        public ChatService(
            IKnowledgeBaseService knowledgeBaseService,
            ILanguageService languageService,
            ILogger<ChatService> logger)
        {
            _kb = knowledgeBaseService;
            _lang = languageService;
            _logger = logger;
        }

        public ChatResponse ProcessMessage(ChatRequest request)
        {
            _logger.LogInformation("Processing message | Session: {Session} | Lang: {Lang}",
                request.SessionId, request.Language);

            // Track session history
            if (!string.IsNullOrEmpty(request.SessionId))
            {
                if (!_sessionHistory.ContainsKey(request.SessionId))
                    _sessionHistory[request.SessionId] = new List<string>();
                _sessionHistory[request.SessionId].Add(request.Message);
            }

            var language = string.IsNullOrEmpty(request.Language) ? "en" : request.Language;
            var query = request.Message?.Trim() ?? "";

            // Handle greetings
            if (IsGreeting(query))
                return BuildGreetingResponse(language, request.SessionId);

            // Handle help requests
            if (IsHelpRequest(query))
                return BuildHelpResponse(language, request.SessionId);

            // Main knowledge base lookup
            var matches = _kb.Search(query, language, 3);

            if (!matches.Any())
                return BuildNotFoundResponse(language, request.SessionId, query);

            var best = matches.First();
            var answer = language == "hi" ? best.AnswerHi : best.AnswerEn;
            var title = language == "hi" ? best.TitleHi : best.TitleEn;

            // Build related topics from related entries
            var relatedTopics = new List<string>();
            if (best.RelatedIds.Any())
            {
                var allEntries = _kb.GetAllEntries();
                relatedTopics = best.RelatedIds
                    .Select(id => allEntries.FirstOrDefault(e => e.Id == id))
                    .Where(e => e != null)
                    .Select(e => language == "hi" ? e!.TitleHi : e!.TitleEn)
                    .Take(3)
                    .ToList();
            }

            return new ChatResponse
            {
                Answer = $"**{title}**\n\n{answer}",
                Category = best.Category,
                Language = language,
                RelatedTopics = relatedTopics,
                PolicyReference = best.PolicyReference,
                Found = true,
                SessionId = request.SessionId
            };
        }

        private bool IsGreeting(string query)
        {
            var greetings = new[] { "hello", "hi", "hey", "namaste", "नमस्ते", "हेलो", "good morning", "good afternoon", "shubh prabhat" };
            return greetings.Any(g => query.ToLower().Contains(g)) && query.Length < 30;
        }

        private bool IsHelpRequest(string query)
        {
            var helpWords = new[] { "help", "what can you do", "guide", "menu", "options", "मदद", "सहायता", "क्या पूछ सकता हूँ" };
            return helpWords.Any(h => query.ToLower().Contains(h));
        }

        private ChatResponse BuildGreetingResponse(string lang, string sessionId)
        {
            var answer = lang == "hi"
                ? "🙏 नमस्ते! मैं IOCL PolicyBot हूँ।\n\nमैं आपको इन विषयों पर जानकारी दे सकता हूँ:\n\n" +
                  "**IT नीतियाँ:**\n- ईमेल नीति\n- इंटरनेट और सोशल मीडिया\n- पासवर्ड नीति\n- डेटा सुरक्षा\n- डिवाइस प्रबंधन\n- VPN और रिमोट वर्क\n\n" +
                  "**CDA नियम:**\n- सामान्य आचरण\n- उपहार और आतिथ्य\n- अनुशासनात्मक कार्यवाही\n- बाहरी रोजगार\n- राजनीतिक गतिविधियाँ\n\nआप हिंदी या अंग्रेजी में प्रश्न पूछ सकते हैं!"
                : "👋 Hello! I'm IOCL PolicyBot.\n\nI can help you with:\n\n" +
                  "**IT Policies:**\n- Email Policy\n- Internet & Social Media\n- Password Policy\n- Data Security\n- Device Management\n- VPN & Remote Work\n\n" +
                  "**CDA Rules:**\n- General Conduct\n- Gifts & Hospitality\n- Disciplinary Proceedings\n- Outside Employment\n- Political Activities\n\nAsk me anything in Hindi or English!";

            return new ChatResponse
            {
                Answer = answer,
                Category = "General",
                Language = lang,
                Found = true,
                SessionId = sessionId
            };
        }

        private ChatResponse BuildHelpResponse(string lang, string sessionId)
        {
            var answer = lang == "hi"
                ? "📋 **आप मुझसे क्या पूछ सकते हैं:**\n\n" +
                  "1️⃣ *\"ईमेल नीति क्या है?\"*\n" +
                  "2️⃣ *\"क्या मैं वेंडर से उपहार ले सकता हूँ?\"*\n" +
                  "3️⃣ *\"पासवर्ड कितने दिनों में बदलना है?\"*\n" +
                  "4️⃣ *\"अनुशासनात्मक कार्यवाही की प्रक्रिया क्या है?\"*\n" +
                  "5️⃣ *\"साइबर हमले में क्या करें?\"*\n" +
                  "6️⃣ *\"CDA नियम के तहत क्या दंड हैं?\"*\n\n" +
                  "बस अपना सवाल टाइप करें!"
                : "📋 **Sample questions you can ask:**\n\n" +
                  "1️⃣ *\"What is the email policy?\"*\n" +
                  "2️⃣ *\"Can I accept gifts from vendors?\"*\n" +
                  "3️⃣ *\"How often must I change my password?\"*\n" +
                  "4️⃣ *\"What is the disciplinary proceedings process?\"*\n" +
                  "5️⃣ *\"What to do in case of a cyber attack?\"*\n" +
                  "6️⃣ *\"What are penalties under CDA rules?\"*\n\n" +
                  "Just type your question!";

            return new ChatResponse
            {
                Answer = answer,
                Category = "Help",
                Language = lang,
                Found = true,
                SessionId = sessionId
            };
        }

        private ChatResponse BuildNotFoundResponse(string lang, string sessionId, string query)
        {
            var answer = lang == "hi"
                ? $"❓ मुझे *\"{query}\"* के बारे में कोई जानकारी नहीं मिली।\n\n" +
                  "कृपया निम्नलिखित में से किसी विषय के बारे में पूछें:\n" +
                  "• ईमेल नीति\n• इंटरनेट/सोशल मीडिया नीति\n• पासवर्ड नीति\n• डेटा सुरक्षा\n" +
                  "• CDA नियम\n• अनुशासनात्मक कार्यवाही\n• उपहार नीति\n• बाहरी रोजगार\n\n" +
                  "या **'मदद'** टाइप करें।"
                : $"❓ I couldn't find information about *\"{query}\"*.\n\n" +
                  "Try asking about:\n" +
                  "• Email Policy\n• Internet/Social Media Policy\n• Password Policy\n• Data Security\n" +
                  "• CDA Rules\n• Disciplinary Proceedings\n• Gift Policy\n• Outside Employment\n\n" +
                  "Or type **'help'** for guidance.";

            return new ChatResponse
            {
                Answer = answer,
                Category = "Not Found",
                Language = lang,
                Found = false,
                SessionId = sessionId
            };
        }
    }
}

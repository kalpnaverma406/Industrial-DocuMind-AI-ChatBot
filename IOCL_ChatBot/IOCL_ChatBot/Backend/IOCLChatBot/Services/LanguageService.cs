namespace IOCLChatBot.Services
{
    public interface ILanguageService
    {
        string DetectLanguage(string text);
        bool IsHindi(string text);
    }

    /// <summary>
    /// Simple language detection service using Unicode range detection.
    /// Detects Hindi (Devanagari script) vs English without any external dependency.
    /// Fully offline.
    /// </summary>
    public class LanguageService : ILanguageService
    {
        // Devanagari Unicode block: U+0900–U+097F
        private const int DevanagariStart = 0x0900;
        private const int DevanagariEnd = 0x097F;

        public bool IsHindi(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return false;

            int devanagariCount = text.Count(c => c >= DevanagariStart && c <= DevanagariEnd);
            int totalChars = text.Count(c => !char.IsWhiteSpace(c));

            if (totalChars == 0) return false;

            // If more than 20% of non-space chars are Devanagari, treat as Hindi
            return (double)devanagariCount / totalChars > 0.2;
        }

        public string DetectLanguage(string text)
        {
            return IsHindi(text) ? "hi" : "en";
        }
    }
}

namespace IOCLChatBot.Models
{
    /// <summary>
    /// A single knowledge base entry covering an IT Policy or CDA Rule
    /// </summary>
    public class KnowledgeEntry
    {
        public string Id { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;         // e.g. "IT Policy", "CDA Rules"
        public string SubCategory { get; set; } = string.Empty;      // e.g. "Email Policy", "Conduct Rules"
        public string PolicyReference { get; set; } = string.Empty;  // e.g. "IT-POL-2023-01"
        public List<string> Keywords { get; set; } = new();          // search triggers
        public List<string> KeywordsHi { get; set; } = new();       // Hindi keywords

        // Bilingual content
        public string TitleEn { get; set; } = string.Empty;
        public string TitleHi { get; set; } = string.Empty;
        public string AnswerEn { get; set; } = string.Empty;
        public string AnswerHi { get; set; } = string.Empty;

        public List<string> RelatedIds { get; set; } = new();
    }
}

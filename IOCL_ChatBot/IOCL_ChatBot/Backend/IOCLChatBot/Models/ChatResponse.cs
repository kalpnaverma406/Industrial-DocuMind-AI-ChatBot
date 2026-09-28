namespace IOCLChatBot.Models
{
    /// <summary>
    /// Response sent back to the Streamlit frontend
    /// </summary>
    public class ChatResponse
    {
        public string Answer { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string Language { get; set; } = "en";
        public List<string> RelatedTopics { get; set; } = new();
        public string PolicyReference { get; set; } = string.Empty;
        public bool Found { get; set; } = true;
        public string SessionId { get; set; } = string.Empty;
    }
}

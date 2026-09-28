namespace IOCLChatBot.Models
{
    /// <summary>
    /// Incoming chat message from the user (Streamlit frontend)
    /// </summary>
    public class ChatRequest
    {
        public string Message { get; set; } = string.Empty;

        /// <summary>
        /// Language: "en" for English, "hi" for Hindi
        /// </summary>
        public string Language { get; set; } = "en";

        public string SessionId { get; set; } = string.Empty;
    }
}

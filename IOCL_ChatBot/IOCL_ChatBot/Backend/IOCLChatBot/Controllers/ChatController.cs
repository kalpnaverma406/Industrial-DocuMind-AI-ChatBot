using Microsoft.AspNetCore.Mvc;
using IOCLChatBot.Models;
using IOCLChatBot.Services;

namespace IOCLChatBot.Controllers
{
    /// <summary>
    /// MVC Controller handling all chat-related API endpoints.
    /// Called by the Streamlit Python frontend.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class ChatController : ControllerBase
    {
        private readonly IChatService _chatService;
        private readonly ILanguageService _languageService;
        private readonly ILogger<ChatController> _logger;

        public ChatController(
            IChatService chatService,
            ILanguageService languageService,
            ILogger<ChatController> logger)
        {
            _chatService = chatService;
            _languageService = languageService;
            _logger = logger;
        }

        /// <summary>
        /// POST /api/chat
        /// Main endpoint for sending a chat message and receiving a policy-aware response.
        /// </summary>
        [HttpPost]
        [ProducesResponseType(typeof(ChatResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public IActionResult PostMessage([FromBody] ChatRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Message))
                return BadRequest(new { error = "Message cannot be empty." });

            // Auto-detect language if not specified
            if (string.IsNullOrEmpty(request.Language))
                request.Language = _languageService.DetectLanguage(request.Message);

            _logger.LogInformation("Chat request | Lang: {Lang} | Query: {Query}",
                request.Language, request.Message);

            var response = _chatService.ProcessMessage(request);
            return Ok(response);
        }

        /// <summary>
        /// GET /api/chat/health
        /// Health check endpoint
        /// </summary>
        [HttpGet("health")]
        public IActionResult HealthCheck()
        {
            return Ok(new
            {
                status = "OK",
                service = "IOCL PolicyBot API",
                timestamp = DateTime.UtcNow,
                version = "1.0.0"
            });
        }
    }
}

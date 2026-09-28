using Microsoft.AspNetCore.Mvc;
using IOCLChatBot.Services;

namespace IOCLChatBot.Controllers
{
    /// <summary>
    /// MVC Controller for browsing the full knowledge base (policy listing).
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class KnowledgeController : ControllerBase
    {
        private readonly IKnowledgeBaseService _kb;

        public KnowledgeController(IKnowledgeBaseService knowledgeBaseService)
        {
            _kb = knowledgeBaseService;
        }

        /// <summary>
        /// GET /api/knowledge
        /// Returns all knowledge base entries (stripped for listing)
        /// </summary>
        [HttpGet]
        public IActionResult GetAll([FromQuery] string? category = null, [FromQuery] string lang = "en")
        {
            var entries = _kb.GetAllEntries();

            if (!string.IsNullOrEmpty(category))
                entries = entries.Where(e => e.Category.ToLower() == category.ToLower()).ToList();

            var result = entries.Select(e => new
            {
                e.Id,
                e.Category,
                e.SubCategory,
                e.PolicyReference,
                Title = lang == "hi" ? e.TitleHi : e.TitleEn,
                Keywords = lang == "hi" ? e.KeywordsHi : e.Keywords
            });

            return Ok(result);
        }

        /// <summary>
        /// GET /api/knowledge/{id}
        /// Returns a single knowledge entry with full bilingual content
        /// </summary>
        [HttpGet("{id}")]
        public IActionResult GetById(string id, [FromQuery] string lang = "en")
        {
            var entry = _kb.GetAllEntries().FirstOrDefault(e => e.Id == id);
            if (entry == null) return NotFound(new { error = $"Entry '{id}' not found." });

            return Ok(new
            {
                entry.Id,
                entry.Category,
                entry.SubCategory,
                entry.PolicyReference,
                Title = lang == "hi" ? entry.TitleHi : entry.TitleEn,
                Answer = lang == "hi" ? entry.AnswerHi : entry.AnswerEn,
                entry.RelatedIds
            });
        }

        /// <summary>
        /// GET /api/knowledge/categories
        /// Returns all available categories
        /// </summary>
        [HttpGet("categories")]
        public IActionResult GetCategories()
        {
            return Ok(_kb.GetCategories());
        }

        /// <summary>
        /// GET /api/knowledge/search?q=...&lang=en
        /// Full-text search across knowledge base
        /// </summary>
        [HttpGet("search")]
        public IActionResult Search([FromQuery] string q, [FromQuery] string lang = "en")
        {
            if (string.IsNullOrWhiteSpace(q))
                return BadRequest(new { error = "Query parameter 'q' is required." });

            var results = _kb.Search(q, lang, 5);
            var mapped = results.Select(e => new
            {
                e.Id,
                e.Category,
                e.SubCategory,
                e.PolicyReference,
                Title = lang == "hi" ? e.TitleHi : e.TitleEn,
                Answer = lang == "hi" ? e.AnswerHi : e.AnswerEn,
            });

            return Ok(mapped);
        }
    }
}

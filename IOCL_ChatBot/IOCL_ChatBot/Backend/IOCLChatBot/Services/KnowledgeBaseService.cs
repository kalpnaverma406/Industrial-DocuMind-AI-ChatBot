using IOCLChatBot.Models;
using Newtonsoft.Json;

namespace IOCLChatBot.Services
{
    /// <summary>
    /// Service responsible for loading and querying the offline knowledge base.
    /// Uses keyword matching with TF-IDF-style scoring for best result retrieval.
    /// </summary>
    public class KnowledgeBaseService : IKnowledgeBaseService
    {
        private readonly List<KnowledgeEntry> _entries;
        private readonly ILogger<KnowledgeBaseService> _logger;

        public KnowledgeBaseService(ILogger<KnowledgeBaseService> logger, IConfiguration config)
        {
            _logger = logger;
            var path = config["AppSettings:KnowledgeBasePath"] ?? "Data/KnowledgeBase.json";

            // Support both relative and absolute paths
            var fullPath = Path.IsPathRooted(path) ? path : Path.Combine(AppContext.BaseDirectory, path);

            // Also try relative to working directory
            if (!File.Exists(fullPath))
                fullPath = Path.Combine(Directory.GetCurrentDirectory(), path);

            if (!File.Exists(fullPath))
            {
                _logger.LogError("KnowledgeBase.json not found at {Path}", fullPath);
                _entries = new List<KnowledgeEntry>();
                return;
            }

            var json = File.ReadAllText(fullPath);
            _entries = JsonConvert.DeserializeObject<List<KnowledgeEntry>>(json) ?? new();
            _logger.LogInformation("Loaded {Count} knowledge base entries", _entries.Count);
        }

        public List<KnowledgeEntry> GetAllEntries() => _entries;

        public List<string> GetCategories() =>
            _entries.Select(e => e.Category).Distinct().ToList();

        /// <summary>
        /// Returns the single best-matching knowledge entry for the given query.
        /// </summary>
        public KnowledgeEntry? FindBestMatch(string query, string language)
        {
            var results = Search(query, language, 1);
            return results.FirstOrDefault();
        }

        /// <summary>
        /// Scores all entries against the query and returns top N results.
        /// Scoring: keyword matches + partial word matches + category matches.
        /// </summary>
        public List<KnowledgeEntry> Search(string query, string language, int topN = 3)
        {
            if (string.IsNullOrWhiteSpace(query)) return new();

            var queryLower = query.ToLower().Trim();
            var queryTokens = Tokenize(queryLower);

            var scored = _entries.Select(entry => new
            {
                Entry = entry,
                Score = CalculateScore(entry, queryLower, queryTokens, language)
            })
            .Where(x => x.Score > 0)
            .OrderByDescending(x => x.Score)
            .Take(topN)
            .Select(x => x.Entry)
            .ToList();

            return scored;
        }

        private double CalculateScore(KnowledgeEntry entry, string queryLower, List<string> queryTokens, string language)
        {
            double score = 0;

            // Choose keyword list based on language
            var keywords = language == "hi"
                ? entry.KeywordsHi.Concat(entry.Keywords).ToList()
                : entry.Keywords;

            // Exact keyword match = highest score
            foreach (var kw in keywords)
            {
                var kwLower = kw.ToLower();
                if (queryLower.Contains(kwLower))
                    score += 10;
                else if (kwLower.Contains(queryLower))
                    score += 7;
                else
                {
                    // Token-level partial matching
                    var kwTokens = Tokenize(kwLower);
                    var commonTokens = queryTokens.Intersect(kwTokens).Count();
                    score += commonTokens * 3;
                }
            }

            // Title match
            var titleToCheck = language == "hi" ? entry.TitleHi : entry.TitleEn;
            if (!string.IsNullOrEmpty(titleToCheck))
            {
                var titleLower = titleToCheck.ToLower();
                foreach (var token in queryTokens)
                {
                    if (titleLower.Contains(token) && token.Length > 2)
                        score += 2;
                }
            }

            // Category match
            if (entry.Category.ToLower().Contains(queryLower) || queryLower.Contains(entry.Category.ToLower()))
                score += 5;

            // SubCategory match
            if (entry.SubCategory.ToLower().Contains(queryLower) || queryLower.Contains(entry.SubCategory.ToLower()))
                score += 4;

            // Answer body match (lower weight to avoid false positives)
            var answerToCheck = language == "hi" ? entry.AnswerHi : entry.AnswerEn;
            if (!string.IsNullOrEmpty(answerToCheck))
            {
                var answerLower = answerToCheck.ToLower();
                var matchCount = queryTokens.Count(t => t.Length > 3 && answerLower.Contains(t));
                score += matchCount * 0.5;
            }

            return score;
        }

        private static List<string> Tokenize(string text)
        {
            return text.Split(new[] { ' ', ',', '.', '?', '!', '/', '\\', '-', '_', ':', ';' },
                             StringSplitOptions.RemoveEmptyEntries)
                       .Where(t => t.Length > 1)
                       .ToList();
        }
    }
}

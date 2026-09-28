using IOCLChatBot.Models;

namespace IOCLChatBot.Services
{
    public interface IKnowledgeBaseService
    {
        List<KnowledgeEntry> GetAllEntries();
        KnowledgeEntry? FindBestMatch(string query, string language);
        List<KnowledgeEntry> Search(string query, string language, int topN = 3);
        List<string> GetCategories();
    }
}

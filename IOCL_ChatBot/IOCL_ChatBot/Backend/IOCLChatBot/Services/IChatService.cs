using IOCLChatBot.Models;

namespace IOCLChatBot.Services
{
    public interface IChatService
    {
        ChatResponse ProcessMessage(ChatRequest request);
    }
}

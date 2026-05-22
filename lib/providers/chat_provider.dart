import 'package:flutter/material.dart';
import 'package:enersense/models/chat_message.dart';
import 'package:enersense/services/api_service.dart';

class ChatProvider extends ChangeNotifier {
  final ApiService apiService;
  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  String? _error;

  ChatProvider({required this.apiService}) {
    // Initialize with greeting messages
    _messages = List.from(ChatMessage.initialMessages);
  }

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Send a user message and get AI response
  Future<void> sendMessage(String userMessage) async {
    // Add user message immediately
    final userMsg = ChatMessage(
      id: 'msg_user_${DateTime.now().millisecondsSinceEpoch}',
      role: 'user',
      content: userMessage,
      timestamp: DateTime.now(),
    );
    _messages.add(userMsg);
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Get AI response
      final aiResponse = await apiService.sendChatMessage(userMessage);
      _messages.add(aiResponse);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Clear chat history
  void clearHistory() {
    _messages = List.from(ChatMessage.initialMessages);
    notifyListeners();
  }

  // Get last AI message for quick suggestions
  ChatMessage? get lastAiMessage {
    try {
      return _messages.lastWhere((m) => m.isAssistant);
    } catch (_) {
      return null;
    }
  }

  // Quick question shortcuts
  void askQuickQuestion(String question) {
    sendMessage(question);
  }
}

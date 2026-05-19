class ChatMessage {
  final String id;
  final String role; // "user" or "assistant"
  final String content;
  final DateTime timestamp;
  final List<String>? suggestions; // For assistant messages with quick reply options

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.suggestions,
  });

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';

  // Parse from API or local storage
  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String? ?? 'msg_${DateTime.now().millisecondsSinceEpoch}',
      role: json['role'] as String? ?? 'assistant',
      content: json['content'] as String? ?? '',
      timestamp: DateTime.tryParse((json['timestamp'] as String?) ?? '') ?? DateTime.now(),
      suggestions: json['suggestions'] != null
          ? List<String>.from(json['suggestions'] as List)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'suggestions': suggestions,
    };
  }

  // Initial greeting messages with suggestions
  static final initialMessages = [
    ChatMessage(
      id: 'msg_initial_1',
      role: 'assistant',
      content: 'Hello! I\'m EnerSense AI. I can help you understand your energy usage and find ways to save money.',
      timestamp: DateTime.now(),
      suggestions: [
        'Why is my bill high this month?',
        'How can I save energy tonight?',
        'Tell me about my AC usage',
        'What\'s my energy score?',
      ],
    ),
  ];
}

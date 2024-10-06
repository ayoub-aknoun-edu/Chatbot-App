import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {
  conversations: any[] = [];
  @Output() conversationSelected = new EventEmitter<number>();
  @Output() toggleSidenav = new EventEmitter<void>();

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.loadConversations();
  }

  loadConversations(): void {
    this.chatService.getConversations().subscribe(
      data => {
        console.log(data.conversations);
        this.conversations = data.conversations.reverse();
        // Select the first conversation by default
        if (this.conversations.length > 0) {
          this.conversationSelected.emit(this.conversations[0].id);
        } else {
          this.createConversation();
        }
      }
    );
  }

  createConversation(): any {
    let name = `New Conversation`
    this.chatService.createConversation(name).subscribe(
      data => {
        console.log(data);
        this.conversations.unshift({ id: data.conversation_id, name: data.name });
        this.conversationSelected.emit(data.conversation_id);
      }
    );
  }

  selectConversation(conversationId: number): void {
    this.conversationSelected.emit(conversationId);
  }

  deleteConversation(event: Event, conversationId: number): void {
    event.stopPropagation(); // Prevent the click event from bubbling up to the list item
    this.chatService.deleteConversation(conversationId).subscribe(
      () => {
        this.conversations = this.conversations.filter(conv => conv.id !== conversationId);
        if (this.conversations.length > 0) {
          this.conversationSelected.emit(this.conversations[0].id);
        } else {
          this.createConversation();
        }
      },
      error => {
        console.error('Error deleting conversation:', error);
      }
    );
  }
}
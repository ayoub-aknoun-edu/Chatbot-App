import { Component, Input, OnChanges, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { ChatService } from '../../services/chat.service';
import { error } from 'node:console';

@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent implements OnChanges, AfterViewChecked {
  @Input() conversationId: number | null = null;
  @ViewChild('messageContainer') private messageContainer!: ElementRef;
  messages: any[] = [];
  userInput: string = '';
  private shouldScrollToBottom = false;

  constructor(private chatService: ChatService) {}

  ngOnChanges(): void {
    if (this.conversationId !== null) {
      this.loadMessages(this.conversationId);
    }
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
    }
  }

  loadMessages(conversationId: number): void {
    this.chatService.getMessages(conversationId).subscribe({
      next: (data:any) => {
        this.messages = data.messages;
        this.shouldScrollToBottom = true;
      },
      error: (error:any) => {
        console.error('There was an error!', error);
      }});
    }
   
    private scrollToBottom(): void {
      try {
        this.messageContainer.nativeElement.scrollTop = this.messageContainer.nativeElement.scrollHeight;
        this.shouldScrollToBottom = false;
      } catch(err) { }
    }
      
  

    sendMessage(): void {
      if (this.userInput.trim() === '' || this.conversationId === null) {
        return;
      }
      let temp = this.userInput;
      this.messages.push({ sender: 'User', message: this.userInput });
      this.userInput = '';
      this.shouldScrollToBottom = true;
      
      this.chatService.sendMessage(this.conversationId, temp).subscribe({
        next: (data) => {
          this.messages.push({ sender: 'AI', message: data.response });
          this.shouldScrollToBottom = true;
        },
        error: (error) => {
          this.messages.pop();
          this.userInput = temp;
          console.error('There was an error!', error);
        }
      });
    }
}

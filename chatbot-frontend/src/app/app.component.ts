import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  selectedConversationId: number | null = null;

  onConversationSelected(conversationId: number): void {
    this.selectedConversationId = conversationId;
  }
}

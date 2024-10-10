// src/app/services/chat.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private baseUrl = 'http://localhost:8000';
  // private baseUrl = 'https://test.elrhadiouini.com/api';


  constructor(private http: HttpClient) {}

  getConversations(): Observable<any> {
    return this.http.get(`${this.baseUrl}/conversations`);
  }

  createConversation(name:string): Observable<any> {

    return this.http.post(`${this.baseUrl}/conversations?name=${name}`, {});
  }

  getMessages(conversationId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/conversations/${conversationId}/messages`);
  }

  sendMessage(conversationId: number, question: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/chat`, { conversation_id: conversationId, question });
  }

  deleteConversation(conversationId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/conversations/${conversationId}`);
  }
}

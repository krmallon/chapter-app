import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  currentUser;

  constructor(private http: HttpClient) {} 

  getCurrentUser(auth0_id) {
      return this.http.get('http://localhost:5000/api/v1.0/auth0/' + auth0_id).subscribe(
          response => {
              sessionStorage.setItem("user_id", this.currentUser)
          }
      )
  }
}

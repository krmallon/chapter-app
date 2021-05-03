import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class ReviewService {
  
  private reviews_private_list;
  private reviewsSubject = new Subject();
  reviews_list = this.reviewsSubject.asObservable();

  private user_review_private_list;
  private userRevSubject = new Subject();
  user_review_list = this.userRevSubject.asObservable();

  constructor(private http: HttpClient) { }

  getReviews(id) {
    return this.http.get(config.app_url + 'books/' + id +'/reviews').subscribe(
        response => {
        this.reviews_private_list = response;
        this.reviewsSubject.next(this.reviews_private_list);
        console.log(response)
        }
    )
}

  getReviewsByUser(user) {
    return this.http.get(config.app_url + 'user/' + user + '/reviews').subscribe(
        response => {
            this.user_review_private_list = response;
            this.userRevSubject.next(this.user_review_private_list);
            // error => console.log(error)
        }
    )
  }

  postReview(isbn, review) {
    let postData = new FormData();

    postData.append("reviewer_id", sessionStorage.user_id);
    // postData.append("book_id", book_id);
    postData.append("text", review.review);
    postData.append("rating", review.rating);
   

    this.http.post(
        config.app_url + 'books/' + isbn + '/reviews',
        postData).subscribe(
        response => {
        // this.getBookID(isbn)
        this.getReviews(isbn);
        } );
}

  deleteReview(review_id) {
    return this.http.delete(config.app_url + 'reviews/'+ review_id).subscribe(response => {
        console.log("Review has been deleted");
    });

}


}

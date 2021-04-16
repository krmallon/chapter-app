import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

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
    return this.http.get('http://localhost:5000/api/v1.0/books/' + id +'/reviews').subscribe(
        response => {
        this.reviews_private_list = response;
        this.reviewsSubject.next(this.reviews_private_list);
        console.log(response)
        }
    )
}

  getReviewsByUser(user) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user + '/reviews/').subscribe(
        response => {
            this.user_review_private_list = response;
            this.userRevSubject.next(this.user_review_private_list);
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
        'http://localhost:5000/api/v1.0/books/' + isbn + '/reviews',
        postData).subscribe(
        response => {
        // this.getBookID(isbn)
        this.getReviews(isbn);
        } );
}

  deleteReview(review_id) {
    return this.http.delete('http://localhost:5000/api/v1.0/reviews/'+ review_id).subscribe(response => {
        console.log("Review has been deleted");
    });

}


}

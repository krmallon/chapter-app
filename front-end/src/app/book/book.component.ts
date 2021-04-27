import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '../auth.service';
import { BookService } from '../services/book.service';
import { LikeService } from '../services/like.service';
import { NotificationService } from '../services/notification.service';
import { ReviewService } from '../services/review.service';

@Component({
  selector: 'app-book',
  templateUrl: './book.component.html',
  styleUrls: ['./book.component.scss']
})
export class BookComponent implements OnInit {

  reviewForm;
  dateForm;
  reviewObjectID = 2

  constructor(public authService: AuthService, public bookService: BookService, public likeService: LikeService, private route: ActivatedRoute, public reviewService: ReviewService,
    private formBuilder: FormBuilder, public notifyService: NotificationService) { }

  ngOnInit(): void {

    this.reviewForm = this.formBuilder.group({
      book_id: ['', Validators.required],
      review: ['', Validators.required],
      rating: [Validators.required]
    });

    this.dateForm = this.formBuilder.group({
      finishMonth: ['', Validators.required],
      finishDay: ['', Validators.required]
    })

    this.bookService.getBook(this.route.snapshot.params.id)
    this.reviewService.getReviews(this.route.snapshot.params.id)
    // this.reviewService.getReviews('0755379926')
    this.bookService.bookPresentInDB(this.route.snapshot.params.id)
  }
  
  

  addToCurrentlyReading(book) {
    this.bookService.addToCurrentlyReading(book.isbn, sessionStorage.user_id)
  }

  addToWantToRead(book) {
    this.bookService.addToWantToRead(book.isbn, sessionStorage.user_id)
  }

  addToHasRead(book) {
    this.bookService.addToHasRead(book.isbn, sessionStorage.user_id)
  }

  addToShelf(shelf, book) {
    if (shelf == 'currentlyreading') {
      this.bookService.addToCurrentlyReading(book.isbn, sessionStorage.user_id)
    } else if (shelf == 'wanttoread') {
      this.bookService.addToWantToRead(book.isbn, sessionStorage.user_id)
    } else if (shelf == 'read') {
      this.bookService.addToHasRead(book.isbn, sessionStorage.user_id)
    }

    this.notifyService.showSuccess('Book added to shelf', 'Success')
  }

  checkInDB(isbn) {
    // debugging method
    console.log(this.bookService.bookInDB)
  }

  addToDB(book) {
    if (!this.bookService.bookInDB) {
      this.bookService.addBookToDB(book)
    }
  }

  postReview() {
    // this.bookService.getBookID(this.route.snapshot.params.id)
    this.reviewService.postReview(this.route.snapshot.params.id, this.reviewForm.value)
    this.reviewForm.reset()
    this.notifyService.showSuccess('Review submitted', 'Success')
  }

  deleteReview(review_id) {
    this.reviewService.deleteReview(review_id)
    this.notifyService.showSuccess('Review deleted', 'Success')
  }

  isOwnReview(review) {
    return review.reviewer_id == sessionStorage.user_id;
  }

  selectDate() {
    console.log(this.dateForm.value)
  }

  likeReview(reviewID) {
    this.likeService.addLike(this.reviewObjectID, reviewID)
    this.reviewService.getReviews(this.route.snapshot.params.id)
  }

  // reviewLiked(reviewID) {
  //   return 
  // }

  // getReviewLikes(reviewID) {
  //   this.likeService.getLikes(this.reviewObjectID, reviewID)
  //   this.reviewService.getReviews(this.route.snapshot.params.id)
  // }

  isInvalid(control) {
    return this.reviewForm.controls[control].invalid &&
           this.reviewForm.controls[control].touched;
  }

  isIncomplete() {
    return this.isInvalid('review') || this.isInvalid('rating') || this.isUnTouched();
  }

  isUnTouched() {
    return this.reviewForm.controls.review.pristine || this.reviewForm.controls.rating.pristine
  }

}

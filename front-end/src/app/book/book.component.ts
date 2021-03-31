import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../auth.service';
import { BookService } from '../services/book.service';
import { ReviewService } from '../services/review.service';

@Component({
  selector: 'app-book',
  templateUrl: './book.component.html',
  styleUrls: ['./book.component.scss']
})
export class BookComponent implements OnInit {

  reviewForm;

  constructor(public authService: AuthService, public bookService: BookService, private route: ActivatedRoute, public reviewService: ReviewService,
    private formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.reviewForm = this.formBuilder.group({
      book_id: ['', Validators.required],
      review: ['', Validators.required],
      rating: 5 
    });

    this.bookService.getBook(this.route.snapshot.params.id)
    this.reviewService.getReviews(this.route.snapshot.params.id)
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
  }

  isOwnReview(review) {
    return review.reviewer_id == sessionStorage.user_id;
  }
}

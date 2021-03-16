import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { BookService } from '../services/book.service';
import { ReviewService } from '../services/review.service';

@Component({
  selector: 'app-book',
  templateUrl: './book.component.html',
  styleUrls: ['./book.component.scss']
})
export class BookComponent implements OnInit {

  reviewForm;

  constructor(public bookService: BookService, private route: ActivatedRoute, public reviewService: ReviewService,
    private formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.reviewForm = this.formBuilder.group({
      book_id: ['', Validators.required],
      review: ['', Validators.required],
      rating: 5 
    });

    this.bookService.getBook(this.route.snapshot.params.id)
    this.reviewService.getReviews(this.route.snapshot.params.id)
    
  }

  print() {
    console.log(this.reviewForm.value)
  }
}

import { Component, OnInit } from '@angular/core';
import { BookService } from '../services/book.service';

@Component({
  selector: 'app-books',
  templateUrl: './books.component.html',
  styleUrls: ['./books.component.scss']
})
export class BooksComponent implements OnInit {

  public sessionStorage = sessionStorage
  shelf = "Currently Reading"

  constructor(public bookService: BookService) { }

  ngOnInit(): void {
    // this.getShelf(this.shelf)
    this.bookService.getCurrentlyReadingByUser(sessionStorage.user_id)
    this.bookService.getHasReadByUser(sessionStorage.user_id)
    this.bookService.getWantsToReadByUser(sessionStorage.user_id)
  }

  // reloadComponent() {
  //   let currentUrl = this.router.url;
  //       this.router.routeReuseStrategy.shouldReuseRoute = () => false;
  //       this.router.onSameUrlNavigation = 'reload';
  //       this.router.navigate([currentUrl]);
  //   }

  setShelf(shelf) {
    this.shelf = shelf
    console.log(this.shelf)
    console.log(typeof this.shelf)
  }

  getShelf(shelf) {
    if (shelf == "Read") {
      this.bookService.getHasReadByUser(sessionStorage.user_id)

    }
    else if (shelf == "Currently Reading") {
      this.bookService.getCurrentlyReadingByUser(sessionStorage.user_id)

    }
    else {
      this.bookService.getWantsToReadByUser(sessionStorage.user_id)
    }
  }

}

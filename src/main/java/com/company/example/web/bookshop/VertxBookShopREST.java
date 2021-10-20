/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
 */

package com.company.example.web.bookshop;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.http.HttpServerResponse;
import io.vertx.core.json.JsonArray;
import io.vertx.core.json.JsonObject;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.RoutingContext;
import io.vertx.ext.web.handler.BodyHandler;

// Import access log handler
// import io.vertx.ext.web.handler.LoggerHandler;

import java.util.HashMap;
import java.util.Map;

public class VertxBookShopREST extends AbstractVerticle {

  private Map<String, JsonObject> books = new HashMap<>();
  private Map<String, JsonObject> carts = new HashMap<>();

  @Override
  public void start() {

    initializeData();

    Router router = Router.router(vertx);

    // Capture access logs
    // router.route().handler(LoggerHandler.create());

    router.route().handler(BodyHandler.create());

    // Books API
    router.get("/books/:bookId").handler(this::handleGetBook);
    router.put("/books/:bookId").handler(this::handleAddBook);
    router.get("/books").handler(this::handleListBooks);

    // Cart API
    router.get("/carts").handler(this::handleListCarts);
    router.get("/carts/:userId").handler(this::handleGetCart);
    router.put("/carts/:userId").handler(this::handleAddCart);
    router.get("/carts/:userId/items").handler(this::handleListCartItems);

    vertx.createHttpServer().requestHandler(router).listen(8080);
  }

  private void handleGetBook(RoutingContext routingContext) {
    String bookId = routingContext.request().getParam("bookId");
    HttpServerResponse response = routingContext.response();

    if (bookId == null) {
      response.setStatusCode(400).end();
    } else {
      JsonObject book = books.get(bookId);
      if (book == null) {
        response.setStatusCode(404).end();
      } else {
        response.putHeader("content-type", "application/json").end(book.encodePrettily());
      }
    }
  }

  private void handleGetCart(RoutingContext routingContext) {
    String userId = routingContext.request().getParam("userId");
    HttpServerResponse response = routingContext.response();

    if (userId == null) {
      response.setStatusCode(400).end();
    } else {
      JsonObject cart = carts.get(userId);
      if (cart == null) {
        response.setStatusCode(404).end();
      } else {
        response.putHeader("content-type", "application/json").end(cart.encodePrettily());
      }
    }
  }

  private void handleAddBook(RoutingContext routingContext) {
    String bookId = routingContext.request().getParam("bookId");
    HttpServerResponse response = routingContext.response();

    if (bookId == null) {
      response.setStatusCode(400).end();
    } else {
      JsonObject book = routingContext.getBodyAsJson();
      if (book == null) {
        response.setStatusCode(400).end();
      } else {
        addBook(book);
        response.end();
      }
    }
  }

  private void handleAddCart(RoutingContext routingContext) {
    String userId = routingContext.request().getParam("userId");
    HttpServerResponse response = routingContext.response();

    if (userId == null) {
      response.setStatusCode(400).end();
    } else {
      JsonObject cart = routingContext.getBodyAsJson();
      if (cart == null) {
        response.setStatusCode(400).end();
      } else {
        addCart(cart);
        response.end();
      }
    }
  }

  private void handleListBooks(RoutingContext routingContext) {
    JsonArray arr = new JsonArray();
    books.forEach((k, v) -> arr.add(v));
    routingContext.response().putHeader("content-type", "application/json").end(arr.encodePrettily());
  }

  private void handleListCarts(RoutingContext routingContext) {
    JsonArray arr = new JsonArray();
    carts.forEach((k, v) -> arr.add(v));
    routingContext.response().putHeader("content-type", "application/json").end(arr.encodePrettily());
  }

  private void handleListCartItems(RoutingContext routingContext) {
    String userId = routingContext.request().getParam("userId");
    HttpServerResponse response = routingContext.response();
    if (userId == null) {
      response.setStatusCode(400).end();
    } else {
      JsonObject cart = carts.get(userId);
      if (cart == null) {
        response.setStatusCode(400).end();
      } else {
        JsonArray items = cart.getJsonArray("items");
        if (items == null) {
          response.setStatusCode(400).end();
        } else {
          response.putHeader("content-type", "application/json").end(items.encodePrettily());
        }
      }
    }
  }

  private void addBook(JsonObject book) {
    books.put(book.getString("book_id"), book);
  }

  private void addCart(JsonObject cart) {
    carts.put(cart.getString("user_id"), cart);
  }

  private void initializeData() {
    // Initialize sample books
    addBook(new JsonObject().put("book_id", "1").put("title", "Anna Karenina").put("author", "Leo Tolstoy").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "2").put("title", "Madame Bovary").put("author", "Gustave Flaubert").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "3").put("title", "War and Peace").put("author", "Leo Tolstoy").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "4").put("title", "The Great Gatsby").put("author", "F. Scott Fitzgerald").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "5").put("title", "Lolita").put("author", "Vladimir Nabokov").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "6").put("title", "Middlemarch").put("author", "George Eliot").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "7").put("title", "The Adventures of Huckleberry Finn").put("author", "Mark Twain").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "8").put("title", "The Stories of Anton Chekhov").put("author", "Anton Chekhov").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "9").put("title", "In Search of Lost Time").put("author", "Marcel Proust").put("genre", "Classics").put("rating", 5.0));
    addBook(new JsonObject().put("book_id", "10").put("title", "Hamlet").put("author", "William Shakespeare").put("genre", "Classics").put("rating", 5.0));

    // Initialize sample carts
    addCart(new JsonObject()
      .put("user_id", "1")
      .put("items", new JsonArray()
        .add(new JsonObject().put("item_id", "1").put("item_count", 2).put("price", 10.99))
        .add(new JsonObject().put("item_id", "2").put("item_count", 4).put("price", 12.99)))
      .put("total", 73.94));

    addCart(new JsonObject()
      .put("user_id", "2")
      .put("items", new JsonArray()
        .add(new JsonObject().put("item_id", "7").put("item_count", 3).put("price", 9.99))
        .add(new JsonObject().put("item_id", "9").put("item_count", 7).put("price", 13.99)))
      .put("total", 127.90));
  }

}

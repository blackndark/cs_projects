# Network

A Twitter-like social network site.

## Technologies

Database implementation: SQLite via Django models  
Backend logic: Python   
Frontend logic: Javascript  
User interface: HTML, Bootstrap  

<img width="1666" alt="Screen Shot 2021-06-21 at 4 01 50 PM" src="https://user-images.githubusercontent.com/817503/122825446-f0715100-d2af-11eb-94c6-2d235173f72c.png">


## Features

#### New Post
- Users who are signed in can write a new text-based post by filling in text into a text area and then clicking a button to submit the post.

#### All Posts
- *All Posts* link in the navigation bar takes the user to a page where they can see all posts from all users, with the most recent posts first.
- Each post has the username of the poster, the post content itself, the date and time at which the post was made, and the number of *likes* the post has.

#### Profile Page
- Clicking on a username loads that user's profile page which shows the number of followers the user has, the number of people that the user follows and all of the posts for that user, in reverse chronological order.
- For any user who is logged in this page displays a *Follow* or *Unfollow* button that will let the current user toggle whether or not they are following this user’s posts.

#### Following
- The *Following* link in the navigation bar (which is only available to logged in users) should take the user to a page where they see all posts made by users that the logged in user follows.

#### Pagination
- Each page is limited to show 10 posts per page. If there are more than 10 posts, a *Next* button appears to take the user to the next page of posts. If the user is not on the first page, a *Previous* button appears to take the user to the previous page of posts.

#### Edit Posts
- Users can click on *Edit* button on their own posts to edit that post. When the user clicks *Edit* button, the content of their post is replaced with a textarea where the user can edit the content of their post. The user should then be able to *Save* the edited post.

#### *Like* and *Unlike*
- Users are able to click a button on any post to toggle whether or not they “like” that post. The like count on the post updates without requiring a reload of the entire page.

## Demo

Live Demo [here](https://youtu.be/YryoBxNN09g)

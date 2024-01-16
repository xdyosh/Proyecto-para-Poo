from googleapiclient.discovery import build
import tkinter as tk
from tkinter import ttk, messagebox

class YouTubeVideo:
    def __init__(self, title, views):
        self.title = title
        self.views = views

class YouTubePlaylist:
    def __init__(self, name, playlist_id):
        self.name = name
        self.playlist_id = playlist_id
        self.videos = []

    def get_playlist_video_info(self, youtube):
        video_info = []
        next_page_token = None

        while True:
            playlist_response = youtube.playlistItems().list(
                playlistId=self.playlist_id,
                part='contentDetails,snippet',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in playlist_response['items']:
                video_title = item['snippet']['title']
                video_statistics = self.get_video_statistics(youtube, item['contentDetails']['videoId'])
                video_info.append(YouTubeVideo(title=video_title, views=video_statistics['viewCount']))

            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

        self.videos = video_info

    def get_video_statistics(self, youtube, video_id):
        video_response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        statistics = video_response['items'][0]['statistics']
        return statistics

class YouTubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Analyzer")

        # Configuración de la interfaz gráfica
        self.api_label = ttk.Label(root, text="Enter API Key:")
        self.api_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.api_entry = ttk.Entry(root, width=30)
        self.api_entry.grid(row=0, column=1, padx=10, pady=10)

        self.playlist_label = ttk.Label(root, text="Enter Playlist ID:")
        self.playlist_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        self.playlist_entry = ttk.Entry(root, width=30)
        self.playlist_entry.grid(row=1, column=1, padx=10, pady=10)

        self.show_views_button = ttk.Button(root, text="Show Views", command=self.show_views)
        self.show_views_button.grid(row=1, column=2, padx=10, pady=10)

        self.clear_api_button = ttk.Button(root, text="Clear API", command=self.clear_api)
        self.clear_api_button.grid(row=0, column=2, padx=10, pady=10)

        self.clear_playlist_button = ttk.Button(root, text="Clear Playlist", command=self.clear_playlist)
        self.clear_playlist_button.grid(row=1, column=3, padx=10, pady=10)

        self.data_tree = ttk.Treeview(root, columns=('Playlist', 'Title', 'Views'), show='headings')
        self.data_tree.heading('Playlist', text='Playlist')
        self.data_tree.heading('Title', text='Title')
        self.data_tree.heading('Views', text='Views')

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.data_tree.yview)
        scrollbar.grid(row=2, column=4, sticky='ns')

        self.data_tree.configure(yscrollcommand=scrollbar.set)

        self.data_tree.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

    def show_views(self):
        api_key = self.api_entry.get()
        playlist_id = self.playlist_entry.get()

        if not api_key:
            messagebox.showerror("Error", "Please enter a valid API Key.")
            return

        if not playlist_id:
            messagebox.showerror("Error", "Please enter a valid YouTube Playlist ID.")
            return

        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            playlist_info = youtube.playlists().list(part='snippet', id=playlist_id).execute()
            playlist_name = playlist_info['items'][0]['snippet']['title']

            playlist = YouTubePlaylist(name=playlist_name, playlist_id=playlist_id)
            playlist.get_playlist_video_info(youtube)
            self.display_data(playlist)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_data(self, playlist):
        self.clear_tree()
        for video in playlist.videos:
            formatted_views = "{:,}".format(int(video.views))  # Formatear el número de vistas
            self.data_tree.insert('', 'end', values=(playlist.name, video.title, formatted_views))

    def clear_tree(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

    def clear_api(self):
        self.api_entry.delete(0, 'end')

    def clear_playlist(self):
        self.playlist_entry.delete(0, 'end')

if __name__ == '__main__':
    root = tk.Tk()
    app = YouTubeApp(root)
    root.mainloop()

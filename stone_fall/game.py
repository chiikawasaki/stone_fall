import pyxel
from fetch_score import fetch_scores_from_api, send_score_to_api
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
STONE_INTERVAL = 30
HEART_INTERVAL = 60
GAME_OVER_DISPLAY_TIMER = 60
START_SCENE = "start"
PLAY_SCENE = "play"
SCORE = 0
PLAYER_NAME = "player"
SCORES = []

class Heart:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 8, 8, 8, pyxel.COLOR_BLACK)

class Stone:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 0, 8, 8, pyxel.COLOR_BLACK)
class App:
    def __init__(self):
        # 初期化
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="サブゲーム")
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        self.is_score_posted = False
        self.is_score_get = False
        self.current_scene = START_SCENE
        self.player_name = PLAYER_NAME
        pyxel.run(self.update, self.draw)

    def reset_play_scene(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT * 4 // 5
        self.stones =[]
        self.hearts = []
        self.score = SCORE
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIMER

    def update_start_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.reset_play_scene()
            self.current_scene = PLAY_SCENE
        if not self.is_score_get:
            global SCORES
            SCORES = fetch_scores_from_api()
            self.is_score_get = True
        # A～Zキーの入力を検知して文字を追加
        for i in range(26):
        # キーが押されたときのみ1文字追加（btnpはキー入力が離されるごとに1度だけ反応）
            if pyxel.btnp(pyxel.KEY_A + i):
                self.player_name += chr(ord('A') + i)

        # バックスペースで最後の文字を削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.player_name = self.player_name[:-1]

    def update_play_scene(self):
        # ゲームオーバー時
        if self.is_collision:
            if not self.is_score_posted:
                send_score_to_api(self.player_name, self.score)
                self.is_score_posted = True  # 一度だけ実行済みとする
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
                self.is_score_posted = False  # 次回のゲーム開始時にリセット
                self.is_score_get = False
                self.player_name = PLAYER_NAME
            return

        # プレイヤーの移動処理
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < SCREEN_WIDTH -16:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 0:
            self.player_x -= 1

        # 石を生成する処理
        if pyxel.frame_count % STONE_INTERVAL == 0:
            self.stones.append(Stone(pyxel.rndi(0,SCREEN_WIDTH -8 ),0))
            
        # ハートを生成する処理
        if pyxel.frame_count % HEART_INTERVAL == 0:
            self.hearts.append(Heart(pyxel.rndi(0,SCREEN_WIDTH -8 ),0))
        # ハートの落下の処理
        for heart in self.hearts.copy():
            heart.update()
            # 当たり判定
            if (self.player_x <= heart.x <= self.player_x + 16 and self.player_y == heart.y + 8):
                self.score += 1
                self.hearts.remove(heart)
                
            if heart.y > SCREEN_HEIGHT:
                self.hearts.remove(heart)

        # 石の落下の処理
        for stone in self.stones.copy():
            stone.update()

            # 当たり判定
            if (self.player_x <= stone.x <= self.player_x + 16 and self.player_y == stone.y + 8):
                self.is_collision = True

            # 画面の外に出た石を削除する処理
            if stone.y > SCREEN_HEIGHT:
                self.stones.remove(stone)


       

    # 1秒間に30回呼び出される関数
    def update(self):
        # 毎フレームごとに呼び出される処理をかく
        if pyxel.btnp(pyxel.KEY_ESCAPE): # ESCAPEキーが押されたら終了
             pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()
        
    def draw_start_scene(self):
        pyxel.blt(0,0,1,0,0,160,120)
        pyxel.text(SCREEN_WIDTH // 10 ,SCREEN_HEIGHT // 10, "Press Enter to Start",pyxel.COLOR_PINK)
        scores = SCORES
        for i, score in enumerate(scores):
                pyxel.text(SCREEN_WIDTH // 10 ,SCREEN_HEIGHT // 10 + 10 + i * 10, f"{score['username']}: {score['score']}",pyxel.COLOR_YELLOW
                )
          
        pyxel.text(SCREEN_WIDTH // 10 ,SCREEN_HEIGHT //10 * 5, "Input Your Name",pyxel.COLOR_RED)
        pyxel.rect(SCREEN_WIDTH // 10,SCREEN_HEIGHT // 10 * 5 + 10, 100 ,10 ,pyxel.COLOR_BLACK)
        pyxel.text(SCREEN_WIDTH //10 ,SCREEN_HEIGHT //10 * 5 +10, self.player_name,pyxel.COLOR_YELLOW)

        
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(SCREEN_WIDTH // 10 ,SCREEN_HEIGHT // 10,"SCORE:" + str(self.score),pyxel.COLOR_YELLOW)
        # 石
        for stone in self.stones:
            stone.draw()
        # ハート
        for heart in self.hearts:
            heart.draw()

        # プレイヤー
        pyxel.blt(self.player_x,self.player_y,0,16,0,16,16 ,pyxel.COLOR_BLACK)
       
        if self.is_collision:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "Game Over", pyxel.COLOR_YELLOW)
        
    # 画面の描画処理
    def draw(self):
        if self.current_scene == PLAY_SCENE:
            self.draw_play_scene()
        elif self.current_scene == START_SCENE:
            self.draw_start_scene()
App()
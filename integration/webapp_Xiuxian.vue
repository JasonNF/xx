<template>
  <div class="xiuxian-container">
    <!-- 顶部导航 -->
    <v-tabs v-model="activeTab" fixed-tabs color="primary">
      <v-tab value="status">角色面板</v-tab>
      <v-tab value="cultivate">修炼</v-tab>
      <v-tab value="battle">历练</v-tab>
      <v-tab value="exchange">兑换</v-tab>
      <v-tab value="rankings">排行榜</v-tab>
    </v-tabs>

    <v-window v-model="activeTab" class="mt-4">
      <!-- 角色面板 -->
      <v-window-item value="status">
        <v-card v-if="player" class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" size="large">mdi-account-circle</v-icon>
            {{ player.name }}
          </v-card-title>
          <v-card-text>
            <v-row dense>
              <v-col cols="6" md="3">
                <div class="stat-item">
                  <div class="stat-label">境界</div>
                  <div class="stat-value primary--text">
                    {{ player.realm }} {{ player.realm_level }}层
                  </div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="stat-item">
                  <div class="stat-label">修为</div>
                  <div class="stat-value">{{ formatNumber(player.cultivation_exp) }}</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="stat-item">
                  <div class="stat-label">灵石</div>
                  <div class="stat-value success--text">{{ formatNumber(player.spirit_stones) }}</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="stat-item">
                  <div class="stat-label">生命值</div>
                  <div class="stat-value">{{ player.hp }} / {{ player.max_hp }}</div>
                </div>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <v-row dense>
              <v-col cols="4">
                <div class="stat-item">
                  <div class="stat-label">攻击</div>
                  <div class="stat-value">{{ player.attack }}</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="stat-item">
                  <div class="stat-label">防御</div>
                  <div class="stat-value">{{ player.defense }}</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="stat-item">
                  <div class="stat-label">战力</div>
                  <div class="stat-value warning--text">
                    {{ player.attack + player.defense + player.comprehension * 10 }}
                  </div>
                </div>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <v-row dense>
              <v-col cols="6">
                <div class="stat-item">
                  <div class="stat-label">悟性</div>
                  <div class="stat-value">{{ player.comprehension }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="stat-item">
                  <div class="stat-label">根骨</div>
                  <div class="stat-value">{{ player.root_bone }}</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="signDaily" :loading="signing" block>
              <v-icon left>mdi-calendar-check</v-icon>
              每日签到
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card v-else>
          <v-card-text class="text-center py-8">
            <v-icon size="64" color="grey">mdi-account-off</v-icon>
            <p class="mt-4 text-h6">角色未创建</p>
            <p class="text-body-2 text--secondary">
              请在 Telegram 使用 /灵根测试 创建角色
            </p>
            <v-btn color="primary" class="mt-4" @click="createPlayer">
              立即创建
            </v-btn>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 修炼面板 -->
      <v-window-item value="cultivate">
        <v-card v-if="player" class="mb-4">
          <v-card-title>
            <v-icon class="mr-2">mdi-meditation</v-icon>
            闭关修炼
          </v-card-title>
          <v-card-text>
            <div v-if="player.is_cultivating">
              <v-alert type="info" class="mb-4">
                <div class="d-flex align-center justify-space-between">
                  <span>正在修炼中...</span>
                  <v-chip color="primary" small>
                    {{ cultivationTimeRemaining }}
                  </v-chip>
                </div>
              </v-alert>
              <v-progress-linear
                :model-value="cultivationProgress"
                color="primary"
                height="25"
                class="mb-4"
              >
                <template v-slot:default>
                  <strong>{{ Math.ceil(cultivationProgress) }}%</strong>
                </template>
              </v-progress-linear>
              <v-btn
                color="success"
                @click="finishCultivation"
                :disabled="cultivationProgress < 100"
                :loading="finishing"
                block
              >
                <v-icon left>mdi-check-circle</v-icon>
                收取修为
              </v-btn>
            </div>
            <div v-else>
              <p class="text-body-2 mb-4">
                选择修炼时长，离线挂机自动获得修为
              </p>
              <v-row dense>
                <v-col cols="6" md="3" v-for="hours in [2, 4, 8, 12]" :key="hours">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    @click="startCultivation(hours)"
                    :loading="cultivating"
                    block
                  >
                    {{ hours }} 小时
                  </v-btn>
                </v-col>
              </v-row>

              <v-divider class="my-4"></v-divider>

              <v-btn
                color="warning"
                @click="breakthrough"
                :loading="breaking"
                block
              >
                <v-icon left>mdi-lightning-bolt</v-icon>
                渡劫突破
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 历练面板 -->
      <v-window-item value="battle">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-sword-cross</v-icon>
            历练战斗
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                cols="12"
                md="6"
                lg="4"
                v-for="monster in monsters"
                :key="monster.id"
              >
                <v-card variant="outlined" :color="monster.is_boss ? 'error' : ''">
                  <v-card-title class="text-h6">
                    {{ monster.name }}
                    <v-chip v-if="monster.is_boss" color="error" size="small" class="ml-2">
                      BOSS
                    </v-chip>
                  </v-card-title>
                  <v-card-subtitle>
                    等级 {{ monster.level }} | {{ monster.realm }}
                  </v-card-subtitle>
                  <v-card-text>
                    <div class="d-flex justify-space-between text-body-2">
                      <span>攻击: {{ monster.attack }}</span>
                      <span>防御: {{ monster.defense }}</span>
                      <span>生命: {{ monster.hp }}</span>
                    </div>
                    <v-divider class="my-2"></v-divider>
                    <div class="text-body-2">
                      <div>奖励:</div>
                      <div class="ml-2">
                        修为: +{{ monster.exp_reward }}
                      </div>
                      <div class="ml-2">
                        灵石: +{{ monster.spirit_stones_reward }}
                      </div>
                    </div>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn
                      color="primary"
                      @click="battle(monster.id)"
                      :loading="battling"
                      :disabled="battleCooldown > 0"
                      block
                    >
                      挑战
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>

            <v-alert v-if="battleCooldown > 0" type="warning" class="mt-4">
              战斗冷却中，还需 {{ battleCooldown }} 秒
            </v-alert>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 兑换面板 -->
      <v-window-item value="exchange">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-cash-multiple</v-icon>
            积分兑换灵石
          </v-card-title>
          <v-card-text>
            <v-alert type="info" class="mb-4">
              <div class="d-flex justify-space-between">
                <span>兑换比例: 10积分 = 1灵石</span>
                <span>最小兑换: 100积分</span>
              </div>
            </v-alert>

            <v-text-field
              v-model.number="exchangeAmount"
              label="兑换积分数量"
              type="number"
              :min="100"
              :step="100"
              outlined
              dense
              suffix="积分"
            >
              <template v-slot:append>
                <v-icon>mdi-arrow-right</v-icon>
                <span class="ml-2 success--text font-weight-bold">
                  {{ Math.floor(exchangeAmount * 0.1) }} 灵石
                </span>
              </template>
            </v-text-field>

            <v-row dense class="mb-4">
              <v-col cols="6" md="3" v-for="amount in [100, 500, 1000, 5000]" :key="amount">
                <v-btn
                  color="primary"
                  variant="outlined"
                  @click="exchangeAmount = amount"
                  block
                  size="small"
                >
                  {{ amount }}
                </v-btn>
              </v-col>
            </v-row>

            <v-btn
              color="success"
              @click="exchange"
              :loading="exchanging"
              :disabled="exchangeAmount < 100"
              block
              large
            >
              <v-icon left>mdi-swap-horizontal</v-icon>
              立即兑换
            </v-btn>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 排行榜 -->
      <v-window-item value="rankings">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-trophy</v-icon>
            排行榜
          </v-card-title>
          <v-card-text>
            <v-tabs v-model="rankingTab" fixed-tabs density="compact">
              <v-tab value="power">战力榜</v-tab>
              <v-tab value="realm">境界榜</v-tab>
            </v-tabs>

            <v-window v-model="rankingTab" class="mt-4">
              <v-window-item value="power">
                <v-list>
                  <v-list-item
                    v-for="(player, index) in powerRankings"
                    :key="index"
                  >
                    <template v-slot:prepend>
                      <v-avatar :color="getRankColor(index)" size="32">
                        {{ index + 1 }}
                      </v-avatar>
                    </template>
                    <v-list-item-title>{{ player.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ player.realm }} {{ player.realm_level }}层
                    </v-list-item-subtitle>
                    <template v-slot:append>
                      <v-chip color="warning" size="small">
                        {{ player.power }} 战力
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>

              <v-window-item value="realm">
                <v-list>
                  <v-list-item
                    v-for="(player, index) in realmRankings"
                    :key="index"
                  >
                    <template v-slot:prepend>
                      <v-avatar :color="getRankColor(index)" size="32">
                        {{ index + 1 }}
                      </v-avatar>
                    </template>
                    <v-list-item-title>{{ player.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      修为: {{ formatNumber(player.cultivation_exp) }}
                    </v-list-item-subtitle>
                    <template v-slot:append>
                      <v-chip color="primary" size="small">
                        {{ player.realm }} {{ player.realm_level }}层
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- 消息提示 -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Xiuxian',
  data() {
    return {
      activeTab: 'status',
      rankingTab: 'power',
      player: null,
      monsters: [],
      powerRankings: [],
      realmRankings: [],

      // 修炼
      cultivating: false,
      finishing: false,
      cultivationProgress: 0,
      cultivationTimeRemaining: '',

      // 突破
      breaking: false,

      // 战斗
      battling: false,
      battleCooldown: 0,

      // 签到
      signing: false,

      // 兑换
      exchanging: false,
      exchangeAmount: 1000,

      // 提示
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',

      // 定时器
      cultivationTimer: null,
      battleCooldownTimer: null,
    }
  },
  mounted() {
    this.loadPlayerInfo()
    this.loadMonsters()
    this.loadRankings()
  },
  beforeUnmount() {
    if (this.cultivationTimer) {
      clearInterval(this.cultivationTimer)
    }
    if (this.battleCooldownTimer) {
      clearInterval(this.battleCooldownTimer)
    }
  },
  methods: {
    async loadPlayerInfo() {
      try {
        const response = await axios.get('/api/xiuxian/player/info')
        this.player = response.data

        // 如果在修炼，启动定时器
        if (this.player.is_cultivating) {
          this.startCultivationTimer()
        }

        // 检查战斗冷却
        if (this.player.last_battle_time) {
          this.checkBattleCooldown()
        }
      } catch (error) {
        if (error.response?.status === 404) {
          this.player = null
        } else {
          this.showError('加载角色信息失败')
        }
      }
    },

    async createPlayer() {
      try {
        const response = await axios.post('/api/xiuxian/player/create')
        this.player = response.data
        this.showSuccess('角色创建成功！')
      } catch (error) {
        this.showError(error.response?.data?.detail || '创建角色失败')
      }
    },

    async loadMonsters() {
      try {
        const response = await axios.get('/api/xiuxian/monsters')
        this.monsters = response.data
      } catch (error) {
        this.showError('加载怪物列表失败')
      }
    },

    async loadRankings() {
      try {
        const [power, realm] = await Promise.all([
          axios.get('/api/xiuxian/rankings/power'),
          axios.get('/api/xiuxian/rankings/realm'),
        ])
        this.powerRankings = power.data
        this.realmRankings = realm.data
      } catch (error) {
        this.showError('加载排行榜失败')
      }
    },

    async startCultivation(hours) {
      this.cultivating = true
      try {
        await axios.post('/api/xiuxian/cultivate/start', null, {
          params: { hours }
        })
        this.showSuccess(`开始 ${hours} 小时闭关修炼`)
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '开始修炼失败')
      } finally {
        this.cultivating = false
      }
    },

    async finishCultivation() {
      this.finishing = true
      try {
        const response = await axios.post('/api/xiuxian/cultivate/finish')
        const data = response.data
        this.showSuccess(
          `${data.message}！获得 ${data.exp_gained} 修为${data.event ? ` (${data.event})` : ''}`
        )
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '收取修为失败')
      } finally {
        this.finishing = false
      }
    },

    async breakthrough() {
      this.breaking = true
      try {
        const response = await axios.post('/api/xiuxian/breakthrough')
        const data = response.data
        if (data.success) {
          this.showSuccess(data.message)
        } else {
          this.showError(data.message)
        }
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '突破失败')
      } finally {
        this.breaking = false
      }
    },

    async battle(monsterId) {
      this.battling = true
      try {
        const response = await axios.post(`/api/xiuxian/battle/${monsterId}`)
        const data = response.data
        if (data.success) {
          this.showSuccess(
            `${data.message}！获得 ${data.exp_gained} 修为，${data.stones_gained} 灵石`
          )
        } else {
          this.showError(`${data.message}，损失 ${data.hp_lost} 生命值`)
        }
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '战斗失败')
      } finally {
        this.battling = false
      }
    },

    async signDaily() {
      this.signing = true
      try {
        const response = await axios.post('/api/xiuxian/sign')
        const data = response.data
        this.showSuccess(`${data.message}！获得 ${data.reward} 灵石`)
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '签到失败')
      } finally {
        this.signing = false
      }
    },

    async exchange() {
      this.exchanging = true
      try {
        const response = await axios.post('/api/xiuxian/exchange', null, {
          params: { credits_amount: this.exchangeAmount }
        })
        const data = response.data
        this.showSuccess(
          `${data.message}！消耗 ${data.credits_used} 积分，获得 ${data.stones_gained} 灵石`
        )
        await this.loadPlayerInfo()
      } catch (error) {
        this.showError(error.response?.data?.detail || '兑换失败')
      } finally {
        this.exchanging = false
      }
    },

    startCultivationTimer() {
      if (this.cultivationTimer) {
        clearInterval(this.cultivationTimer)
      }

      this.cultivationTimer = setInterval(() => {
        const startTime = new Date(this.player.cultivation_start_time)
        const duration = this.player.cultivation_duration * 60 * 60 * 1000
        const finishTime = new Date(startTime.getTime() + duration)
        const now = new Date()
        const remaining = finishTime - now

        if (remaining <= 0) {
          this.cultivationProgress = 100
          this.cultivationTimeRemaining = '修炼完成'
          clearInterval(this.cultivationTimer)
        } else {
          this.cultivationProgress = ((duration - remaining) / duration) * 100
          const minutes = Math.floor(remaining / 60000)
          const seconds = Math.floor((remaining % 60000) / 1000)
          this.cultivationTimeRemaining = `${minutes}分${seconds}秒`
        }
      }, 1000)
    },

    checkBattleCooldown() {
      const lastBattle = new Date(this.player.last_battle_time)
      const cooldown = 5 * 60 * 1000 // 5分钟
      const now = new Date()
      const remaining = cooldown - (now - lastBattle)

      if (remaining > 0) {
        this.battleCooldown = Math.ceil(remaining / 1000)
        this.battleCooldownTimer = setInterval(() => {
          this.battleCooldown--
          if (this.battleCooldown <= 0) {
            clearInterval(this.battleCooldownTimer)
          }
        }, 1000)
      }
    },

    formatNumber(num) {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num
    },

    getRankColor(index) {
      if (index === 0) return 'amber'
      if (index === 1) return 'grey'
      if (index === 2) return 'brown'
      return 'blue-grey'
    },

    showSuccess(message) {
      this.snackbarText = message
      this.snackbarColor = 'success'
      this.snackbar = true
    },

    showError(message) {
      this.snackbarText = message
      this.snackbarColor = 'error'
      this.snackbar = true
    },
  },
}
</script>

<style scoped>
.xiuxian-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

.stat-item {
  text-align: center;
  padding: 8px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}
</style>

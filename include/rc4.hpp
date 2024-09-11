#include <vector>
#include <array>
#include <cstdint>
#include <algorithm>
// using namespace std;
class RC4 {
    
    public:
        explicit RC4(void) {};
        void reset(const std::vector<uint8_t> &key, size_t len);
        void crypt(const std::vector<uint8_t> &in, std::vector<uint8_t> &out, size_t len);
        ~RC4(void) {};

    private:
        std::array<uint8_t, 256> sbox;
        uint8_t idx1;
        uint8_t idx2;
        explicit RC4(const RC4&) = delete;
        explicit RC4(const RC4&&) = delete;
        const RC4& operator=(const RC4&) = delete;
        const RC4&& operator=(const RC4&&) = delete;
};

void RC4::reset(const std::vector<uint8_t> &key, size_t len) {
    uint8_t j = 0;

    for (auto i = 0; i < sbox.size(); i++)
        sbox[i] = i;
    idx1 = 0; idx2 = 0;

    for (auto i = 0; i < sbox.size(); i++) {
        j += sbox[i] + key[i % len];
        std::swap(sbox[i], sbox[j]);
    }
}

void RC4::crypt(const std::vector<uint8_t> &in, std::vector<uint8_t> &out, size_t len) {
    uint8_t j = 0;

    for (auto i = 0; i < len; i++) {
        idx1++; idx2 += sbox[idx1];
        std::swap(sbox[idx1], sbox[idx2]);
        j = sbox[idx1] + sbox[idx2];
        out[i] = in[i] ^ sbox[j];
    }
}

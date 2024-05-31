#include<bits/stdc++.h>
#include<filesystem>
#include<openssl/sha.h>

// function to create hash of a file
inline std::string SHA256(const char* const path) {
    std::ifstream fp(path, std::ios::in | std::ios::binary);

    if (not fp.good()) {
        std::ostringstream os;
        os << "Cannot open \"" << path << "\": " << std::strerror(errno) << ".";
        throw std::runtime_error(os.str());
    }

    constexpr const std::size_t buffer_size { 1 << 12 };
    char buffer[buffer_size];

    unsigned char hash[SHA256_DIGEST_LENGTH] = { 0 };

    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    while (fp.good()) {
        fp.read(buffer, buffer_size);
        SHA256_Update(&ctx, buffer, fp.gcount());
    }

    SHA256_Final(hash, &ctx);
    fp.close();

    std::ostringstream os;
    os << std::hex << std::setfill('0');

    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        os << std::setw(2) << static_cast<unsigned int>(hash[i]);
    }

    return os.str();
}

// create hash of every file in directory and subdirectories
int main(int argc, char *argv[]) {
    if (argc != 2){
        std::cerr << "usage: " << argv[0] << " [ABSOLUTE PATH OF DIRECTORY]" << std::endl;
    }

    for (const auto& p : std::filesystem::recursive_directory_iterator(argv[1])) {
        if (!std::filesystem::is_directory(p)) {
            continue;
        }

        try {
            // TODO : finish this part and add events
            std::cout << SHA256(p.path().c_str()) << " " << "filename" << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "[fatal] " <<  e.what() << std::endl;
        }
    }

    return 0;
}
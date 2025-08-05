import User from "../models/user_model.mjs";
import pbkdf2 from "crypto";

// Function to handle user login via email
export async function login(req, res) {
  try {
    const { email, password } = req.body;

    console.log("Login request received:", { email, password });

    // Validate input
    if (!email || !password) {
      return res
        .status(400)
        .json({
          success: false,
          message: "Email and password are required.",
        });
    }

    // Logic to authenticate user (replace with actual implementation)
    const user = await User.findOne({ email });

    // Generate hash using the salt from the user object and compare with stored hash
    if (!user) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid email or password." });
    }

    const inputHash = pbkdf2
      .pbkdf2Sync(password, user.salt + user.email + ":", 1000, 64, "sha512")
      .toString("base64");

    if (inputHash !== user.passwordHash) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid email or password." });
    }

    // Return success response
    return res
      .status(200)
      .json({
        success: true,
        message: "Login successful",
        data: { username: user.username, email: user.email, user_id: user._id },
      });
  } catch (error) {
    console.error("Login error:", error);
    return res.status(500).json({ success: false, message: error.message });
  }
}

// Function to handle user signup
export async function signup(req, res) {
  try {
    const { username, email, password } = req.body;

    // Validate input
    if (!username || !email || !password) {
      return res
        .status(400)
        .json({
          success: false,
          message: "Username, email, and password are required.",
        });
    }

    // Logic to create a new user (replace with actual implementation)
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res
        .status(409)
        .json({ success: false, message: "Email already exists." });
    }

    // Generate a salt and hash the password
    const salt = pbkdf2.randomBytes(16).toString("base64");
    const passwordHash = pbkdf2
      .pbkdf2Sync(password, salt + email + ":", 1000, 64, "sha512")
      .toString("base64");

    // Create a new user object
    const newUser = new User({
      username,
      email,
      salt,
      passwordHash,
    });

    console.log("User : ", newUser);

    // Save the new user to the database
    await newUser.save();

    // Return success response
    return res
      .status(201)
      .json({ success: true, message: "Signup successful", data: newUser });
  } catch (error) {
    console.error("Signup error:", error);
    return res.status(500).json({ success: false, message: error.message });
  }
}

const AUTH_FNS = {
  login,
  signup,
};

export default AUTH_FNS;
